import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='mbtiles-s3-server',
    version='0.0.15',
    author='Department for International Trade',
    author_email='sre@digital.trade.gov.uk',
    description='Server to on-the-fly extract and serve vector tiles from an mbtiles file on S3',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/uktrade/mbtiles-s3-server',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: BSD License',
    ],
    python_requires='>=3.7.0',
    install_requires=[
        'flask>=2.0.3',
        'gevent>=21.12.0',
        'protobuf>=3.0.0',
        'sqlite-s3-query>=0.0.68',
    ],
    packages=[
        'mbtiles_s3_server',
    ],
    include_package_data=True,
)
