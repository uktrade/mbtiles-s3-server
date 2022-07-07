import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='mbtiles-s3-server',
    version='0.0.1',
    author='Department for International Trade',
    author_email='sre@digital.trade.gov.uk',
    description='Server to on-the-fly extract and serve vector tiles from an mbtiles file on S3',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/uktrade/mbtiles-s3-server',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.5.0',
    install_requires=[
        'flask>=2.1.2',
        'gevent>=21.12.0',
        'sqlite-s3-query>=0.0.67',
    ],
    py_modules=[
        'mbtiles_s3_server',
    ],
)
