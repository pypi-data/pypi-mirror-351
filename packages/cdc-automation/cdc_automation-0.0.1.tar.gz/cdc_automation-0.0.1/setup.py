import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdc-automation",
    version="0.0.1",
    author="Wayne Chen",
    author_email="kensmart123@yahoo.com.tw",
    description="this is example",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'jsonschema',
        'webcolors',  # jsonschema validating formats
        'rfc3339-validator',  # jsonschema validating formats
        'isoduration',  # jsonschema validating formats
        'fqdn',  # jsonschema validating formats
        'idna',  # jsonschema validating formats
        'rfc3987',  # jsonschema validating formats
        'jsonpointer',  # jsonschema validating formats
        'uri-template',  # jsonschema validating formats
        'pycryptodome',  # handle AES, RSA crypto
    ]
)