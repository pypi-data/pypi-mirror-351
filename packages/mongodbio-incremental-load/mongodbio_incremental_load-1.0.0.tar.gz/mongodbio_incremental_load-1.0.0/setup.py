from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: Apache Software License',
  'Operating System :: OS Independent',
  'Programming Language :: Python :: 3'
]

setup(
  name='mongodbio-incremental-load',
  version='1.0.0',
  description='Apache-beam mongodbio with custom date range filter field',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://github.com/KaranratRatta/mongodbio-incremental-load',  
  author='Karanrat Rattanawichai',
  author_email='karanrat.rattanawichai@gmail.com',
  classifiers=classifiers,
  keywords=['Apache', 'Beam', 'python', 'mongodbio'],
  packages=find_packages(),
  install_requires=[
    'apache-beam',
    'pymongo'
  ]
)