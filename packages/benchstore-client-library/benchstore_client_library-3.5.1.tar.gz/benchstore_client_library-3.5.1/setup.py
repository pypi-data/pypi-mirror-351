
from setuptools import setup, find_packages

long_description = """
The benchstore-client-library is a robust Python library designed to streamline the collection, 
storage, and retrieval of benchmarking results. It addresses the common challenge developers and 
performance engineers face when handling large volumes of benchmark data—efficient organization 
and quick access.
"""


setup(
    name='benchstore_client_library',
    version='3.5.1',
    packages=find_packages(),
    description='benchstore_client_library',
    long_description_content_type='text/plain',
    long_description=long_description,
    url='https://github.com/staticafi/BenchStore/',
    download_url='https://github.com/staticafi/BenchStore/',
    project_urls={
        'Documentation': 'https://github.com/staticafi/BenchStore/'},
    author='Tom Christian',
    author_email='tom.christian@openxta.com',
    python_requires='>=3.6',
    platforms=['Linux'],
    license='BSD',
    install_requires=[
        'requests',
        'cpjson',
        'certifi'
    ],
)
