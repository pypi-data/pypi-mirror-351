#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements...  (license text unchanged)
#

"""This module implements IO classes to read and write data on MongoDB,
but now uses `timestamp` (a datetime field) as the split key instead of `_id`.
"""

# pytype: skip-file

import itertools
import json
import logging
import math
import struct
import datetime
from typing import Union

import apache_beam as beam
from apache_beam.io import iobase
from apache_beam.io.range_trackers import (
    LexicographicKeyRangeTracker,
    OffsetRangeTracker,
    OrderedPositionRangeTracker,
)
from apache_beam.transforms import DoFn, PTransform, Reshuffle

_LOGGER = logging.getLogger(__name__)

try:
    from bson import json_util, objectid
    from bson.objectid import ObjectId
    from pymongo import ASCENDING, DESCENDING, MongoClient, ReplaceOne
except ImportError:
    objectid = None
    json_util = None
    ObjectId = None
    ASCENDING = 1
    DESCENDING = -1
    MongoClient = None
    ReplaceOne = None
    _LOGGER.warning("Could not find a compatible bson package.")

__all__ = ["ReadFromMongoDB", "WriteToMongoDB"]
class ReadFromMongoDB(PTransform):
    """A ``PTransform`` to read MongoDB documents by `timestamp` into a PCollection."""
    def __init__(
        self,
        uri="mongodb://localhost:27017",
        db=None,
        coll=None,
        filter=None,
        projection=None,
        extra_client_params=None,
        bucket_auto=False,
        timestamp_field="updated_at",
    ):
        if extra_client_params is None:
            extra_client_params = {}
        if not isinstance(db, str):
            raise ValueError("ReadFromMongoDB db param must be specified as a string")
        if not isinstance(coll, str):
            raise ValueError("ReadFromMongoDB coll param must be specified as a string")
        self._mongo_source = _BoundedMongoSource(
            uri=uri,
            db=db,
            coll=coll,
            filter=filter,
            projection=projection,
            extra_client_params=extra_client_params,
            bucket_auto=bucket_auto,
            timestamp_field=timestamp_field,
        )

    def expand(self, pcoll):
        return pcoll | iobase.Read(self._mongo_source)

class _DateTimeHelper:
    @classmethod
    def datetime_to_millis(cls, dt: datetime.datetime) -> int:
        """Convert datetime to milliseconds since epoch (UTC assumed)."""
        # convert to UTC timestamp float seconds
        ts = dt.timestamp()
        # convert to integer milliseconds
        return int(ts * 1000)

    @classmethod
    def millis_to_datetime(cls, ms: int) -> datetime.datetime:
        """Convert milliseconds since epoch to datetime."""
        # convert ms to seconds float
        ts = ms / 1000.0
        return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)

    @classmethod
    def increment_millis(cls, dt: datetime.datetime, ms: int = 1) -> datetime.datetime:
        """Increment datetime by ms milliseconds."""
        return dt + datetime.timedelta(milliseconds=ms)


class _DateTimeRangeTracker(OrderedPositionRangeTracker):
    def position_to_fraction(
        self,
        pos: datetime.datetime,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> float:
        start_ms = _DateTimeHelper.datetime_to_millis(start)
        end_ms = _DateTimeHelper.datetime_to_millis(end)
        pos_ms = _DateTimeHelper.datetime_to_millis(pos)
        return (pos_ms - start_ms) / (end_ms - start_ms)

    def fraction_to_position(
        self,
        fraction: float,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> datetime.datetime:
        if fraction <= 0.0:
            return start
        if fraction >= 1.0:
            return _DateTimeHelper.increment_millis(end, -1)

        start_ms = _DateTimeHelper.datetime_to_millis(start)
        end_ms = _DateTimeHelper.datetime_to_millis(end)

        total_ms = end_ms - start_ms
        offset_ms = int(total_ms * fraction)

        candidate_ms = start_ms + offset_ms
        if candidate_ms >= end_ms:
            candidate_ms = end_ms - 1

        return _DateTimeHelper.millis_to_datetime(candidate_ms)
    
    def fraction_to_position(
        self,
        fraction: float,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> datetime.datetime:
        start_ts = _DateTimeHelper.datetime_to_millis(start)
        end_ts = _DateTimeHelper.datetime_to_millis(end)
        total = end_ts - start_ts
        pos_ts = start_ts + total * fraction
        # clamp between start and end
        if pos_ts <= start_ts:
            return _DateTimeHelper.increment_millis(start, 1)
        if pos_ts >= end_ts:
            return _DateTimeHelper.increment_millis(end, -1)
        return _DateTimeHelper.millis_to_datetime(pos_ts)


class _BoundedMongoSource(iobase.BoundedSource):
    """A MongoDB source that reads a finite amount of input records by timestamp."""
    def __init__(
        self,
        uri=None,
        db=None,
        coll=None,
        filter=None,
        projection=None,
        extra_client_params=None,
        bucket_auto=False,
        timestamp_field="updated_at",
    ):
        if extra_client_params is None:
            extra_client_params = {}
        if filter is None:
            filter = {}
        self.uri = uri
        self.db = db
        self.coll = coll
        self.filter = filter
        self.projection = projection
        self.spec = extra_client_params
        self.bucket_auto = bucket_auto
        self.timestamp_field = timestamp_field

    def estimate_size(self):
        with MongoClient(self.uri, **self.spec, datetime_conversion='DATETIME_AUTO') as client:
            return client[self.db].command("collstats", self.coll).get("size")

    def _estimate_average_document_size(self):
        with MongoClient(self.uri, **self.spec, datetime_conversion='DATETIME_AUTO') as client:
            return client[self.db].command("collstats", self.coll).get("avgObjSize")

    def split(
        self,
        desired_bundle_size: int,
        start_position: Union[int, str, bytes, datetime.datetime] = None,
        stop_position: Union[int, str, bytes, datetime.datetime] = None,
    ):
        desired_mb = max(desired_bundle_size // (1 << 20), 1)
        is_initial = (start_position is None and stop_position is None)
        start_position, stop_position = self._replace_none_positions(
            start_position, stop_position
        )

        if self.bucket_auto:
            # $bucketAuto on timestamp
            _LOGGER.info("Using bucketAuto")
            _LOGGER.info(f"split : {self.timestamp_field}")
            split_keys = []
            weights = []
            for bucket in self._get_auto_buckets(
                desired_mb, start_position, stop_position, is_initial
            ):
                split_keys.append({self.timestamp_field: bucket["_id"]["max"]})
                weights.append(bucket["count"])
        else:
            # splitVector on timestamp
            _LOGGER.info("Using splitVector")
            raw_keys = self._get_split_keys(desired_mb, start_position, stop_position)
            split_keys = [{self.timestamp_field: k[self.timestamp_field]} for k in raw_keys]
            
            weights = itertools.cycle((desired_mb,))

        bundle_start = start_position
        for sk, weight in zip(split_keys, weights):
            if bundle_start >= stop_position:
                break
            bundle_end = min(stop_position, sk[self.timestamp_field])
            yield iobase.SourceBundle(
                weight=weight,
                source=self,
                start_position=bundle_start,
                stop_position=bundle_end,
            )
            bundle_start = bundle_end

        if bundle_start < stop_position:
            weight = 1 if self.bucket_auto else desired_mb
            yield iobase.SourceBundle(
                weight=weight,
                source=self,
                start_position=bundle_start,
                stop_position=stop_position,
            )

    def get_range_tracker(
        self,
        start_position: Union[int, str, datetime.datetime] = None,
        stop_position: Union[int, str, datetime.datetime] = None,
    ):
        start_position, stop_position = self._replace_none_positions(
            start_position, stop_position
        )

        # datetime first
        if isinstance(start_position, datetime.datetime):
            return _DateTimeRangeTracker(start_position, stop_position)

        # fall back to int or str if you really need
        if isinstance(start_position, int):
            return OffsetRangeTracker(start_position, stop_position)
        if isinstance(start_position, str):
            return LexicographicKeyRangeTracker(start_position, stop_position)

        raise NotImplementedError(f"RangeTracker for {type(start_position)} not implemented!")

    def read(self, range_tracker):
        # Log the start of the read operation
        logging.info("Starting read operation with range: %s - %s",
                    range_tracker.start_position(), range_tracker.stop_position())
        
        # Check the value of self.timestamp_field
        _LOGGER.info(f"read: Using timestamp field: {self.timestamp_field}")
        _LOGGER.info(f"read: self.bucket_auto: {self.bucket_auto}")
        _LOGGER.info(f"read: self: {self}")
        
        with MongoClient(self.uri, **self.spec, datetime_conversion='DATETIME_AUTO') as client:
            all_filters = self._merge_field_filter(
                range_tracker.start_position(), range_tracker.stop_position()
            )
            _LOGGER.info("Using filter: %s", all_filters)

            cursor = client[self.db][self.coll] \
                          .find(filter=all_filters, projection=self.projection) \
                          .sort([(self.timestamp_field, ASCENDING)])
            for doc in cursor:
                if not range_tracker.try_claim(doc[self.timestamp_field]):
                    return
                yield doc

    def display_data(self):
        dd = super().display_data()
        dd.update({
            "database": self.db,
            "collection": self.coll,
            "filter": json.dumps(self.filter, default=json_util.default),
            "projection": str(self.projection),
            "bucket_auto": self.bucket_auto,
            "split_field": self.timestamp_field,
        })
        return dd

    def _range_is_not_splittable(self, start, end):
        # single document cannot split
        return isinstance(start, datetime.datetime) and start >= _DateTimeHelper.increment_millis(end, -1)

    def _get_split_keys(self, mb, start, end):
        if self._range_is_not_splittable(start, end):
            return []
        with MongoClient(self.uri, **self.spec, datetime_conversion='DATETIME_AUTO') as client:
            ns = f"{self.db}.{self.coll}"
            res = client[self.db].command(
                "splitVector",
                ns,
                keyPattern={self.timestamp_field: 1},
                min={self.timestamp_field: start},
                max={self.timestamp_field: end},
                maxChunkSize=mb,
            )["splitKeys"]
            # each key is like {self.timestamp_field: ...}
            return res

    def _get_auto_buckets(self, mb, start, end, initial):
        if self._range_is_not_splittable(start, end):
            _LOGGER.info(f"_get_auto_buckets : _range_is_not_splittable")
            return []
        
        if initial and not self.filter:
            size_mb = self.estimate_size() / float(1 << 20)
        else:
            cnt = self._count_field_range(start, end)
            avg = self._estimate_average_document_size()
            size_mb = cnt * avg / float(1 << 20)
        
        if size_mb == 0:
            _LOGGER.info(f"size_mb == 0")
            return []
        
        pipeline = [
            {"$match": self._merge_field_filter(start, end)},
            {"$bucketAuto": {"groupBy": f"${self.timestamp_field}", "buckets": math.ceil(size_mb / mb)}}
        ]
        
        # Log the aggregation query
        _LOGGER.info(f"Aggregation query: {pipeline}")
        
        buckets = list(
            MongoClient(self.uri, **self.spec, datetime_conversion='DATETIME_AUTO')[self.db][self.coll]
                .aggregate(pipeline, allowDiskUse=True)
        )
        
        if buckets:
            buckets[-1]["_id"]["max"] = end
        
        return buckets

    def _merge_field_filter(self, start, stop=None):
        # Check if self.timestamp_field is None and raise an error if it is
        # if self.timestamp_field is None:
        #     raise ValueError("timestamp_field cannot be None")
        
        # Use the dynamic field name (self.timestamp_field) for filtering
        if stop is None:
            fld = {self.timestamp_field: {"$gte": start}}  # Dynamic field name
        else:
            fld = {self.timestamp_field: {"$gte": start, "$lt": stop}}  # Dynamic field name
        
        if self.filter:
            return {"$and": [self.filter.copy(), fld]}
        return fld

    def _get_head_timestamp(self, sort_order):
        with MongoClient(self.uri, **self.spec, datetime_conversion='DATETIME_AUTO') as client:
            cursor = client[self.db][self.coll] \
                         .find(filter={}, projection=[self.timestamp_field]) \
                         .sort([(self.timestamp_field, sort_order)]) \
                         .limit(1)
            try:
                return cursor[0][self.timestamp_field]
            except IndexError:
                raise ValueError("Empty MongoDB collection")

    def _replace_none_positions(self, start, stop):
        if start is None:
            start = self._get_head_timestamp(ASCENDING)
        if stop is None:
            last = self._get_head_timestamp(DESCENDING)
            stop = _DateTimeHelper.increment_millis(last, 1)
        # No truncation needed, everything will be consistent now
        return start, stop


    def _count_field_range(self, start, stop):
        with MongoClient(self.uri, **self.spec, datetime_conversion='DATETIME_AUTO') as client:
            return client[self.db][self.coll].count_documents(
                filter=self._merge_field_filter(start, stop)
            )


# The WriteToMongoDB transform remains unchanged; it still writes by _id
class WriteToMongoDB(PTransform):
    """(unchanged)"""
    def __init__(self, uri="mongodb://localhost:27017", db=None, coll=None,
                 batch_size=100, extra_client_params=None):
        if extra_client_params is None:
            extra_client_params = {}
        if not isinstance(db, str):
            raise ValueError("WriteToMongoDB db param must be specified as a string")
        if not isinstance(coll, str):
            raise ValueError("WriteToMongoDB coll param must be specified as a string")
        self._uri = uri
        self._db = db
        self._coll = coll
        self._batch_size = batch_size
        self._spec = extra_client_params

    def expand(self, pcoll):
        return (
            pcoll
            | beam.ParDo(_GenerateObjectIdFn())
            | Reshuffle()
            | beam.ParDo(
                _WriteMongoFn(
                    self._uri, self._db, self._coll, self._batch_size, self._spec
                )
            )
        )


class _GenerateObjectIdFn(DoFn):
    def process(self, element, *args, **kwargs):
        if "_id" not in element:
            element["_id"] = objectid.ObjectId()
        yield element


class _WriteMongoFn(DoFn):
    def __init__(self, uri=None, db=None, coll=None, batch_size=100, extra_params=None):
        if extra_params is None:
            extra_params = {}
        self.uri = uri
        self.db = db
        self.coll = coll
        self.spec = extra_params
        self.batch_size = batch_size
        self.batch = []

    def finish_bundle(self):
        self._flush()

    def process(self, element, *args, **kwargs):
        self.batch.append(element)
        if len(self.batch) >= self.batch_size:
            self._flush()

    def _flush(self):
        if not self.batch:
            return
        with _MongoSink(self.uri, self.db, self.coll, self.spec) as sink:
            sink.write(self.batch)
            self.batch = []

    def display_data(self):
        res = super().display_data()
        res["database"] = self.db
        res["collection"] = self.coll
        res["batch_size"] = self.batch_size
        return res


class _MongoSink:
    def __init__(self, uri=None, db=None, coll=None, extra_params=None):
        if extra_params is None:
            extra_params = {}
        self.uri = uri
        self.db = db
        self.coll = coll
        self.spec = extra_params
        self.client = None

    def write(self, documents):
        if self.client is None:
            self.client = MongoClient(host=self.uri, **self.spec, datetime_conversion='DATETIME_AUTO')
        requests = [
            ReplaceOne(filter={"_id": doc.get("_id", None)},
                       replacement=doc,
                       upsert=True)
            for doc in documents
        ]
        resp = self.client[self.db][self.coll].bulk_write(requests)
        _LOGGER.debug(
            "BulkWrite to MongoDB result in nModified:%d, nUpserted:%d, nMatched:%d, Errors:%s"
            % (
                resp.modified_count,
                resp.upserted_count,
                resp.matched_count,
                resp.bulk_api_result.get("writeErrors"),
            )
        )

    def __enter__(self):
        if self.client is None:
            self.client = MongoClient(host=self.uri, **self.spec, datetime_conversion='DATETIME_AUTO')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None:
            self.client.close()
