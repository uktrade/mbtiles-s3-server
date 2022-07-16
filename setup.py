import setuptools


def contents(file_name):
    with open(file_name, 'r') as file:
        return file.read()


setuptools.setup(
    name='mbtiles-s3-server',
    version='0.0.17',
    author='Department for International Trade',
    author_email='sre@digital.trade.gov.uk',
    description='Server to on-the-fly extract and serve vector tiles from an mbtiles file on S3',
    long_description=contents('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/uktrade/mbtiles-s3-server',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: BSD License',
    ],
    python_requires='>=3.7.4',
    install_requires=[
        line for line in
        contents('requirements.txt').splitlines()
        if line and not line.startswith('#')
    ],
    packages=[
        'mbtiles_s3_server',
    ],
    include_package_data=True,
)
