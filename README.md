# Welcome to gcs_lock_thing


[![image](https://img.shields.io/pypi/v/gcs_lock_thing.svg)](https://pypi.python.org/pypi/gcs_lock_thing)


**Basic mutex lock implementation with Google Cloud Storage with ttl and exponential backoff**


-   Free software: MIT license
-   Documentation: <https://connor-ps.github.io/gcs_lock_thing>
    

## Features

-   Basic mutex lock in GCP

## Credits

This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [giswqs/pypackage](https://github.com/giswqs/pypackage) project template.

# Installation

## Stable release

To install gcs-lock-thing, run this command in your terminal:

```
pip install gcs_lock_thing
```

This is the preferred method to install gcs-lock-thing, as it will always install the most recent stable release.

If you don't have [pip](https://pip.pypa.io) installed, this [Python installation guide](http://docs.python-guide.org/en/latest/starting/installation/) can guide you through the process.


# Usage

To use gcs-lock-thing in a project:

```python
import gcs_lock_thing.lock as gcs

public_bucket_path = "data-trf-test-mutex-lock"
client = gcs.Client(bucket=public_bucket_path, lock_file_path="test-lock.txt", ttl=2)

# get lock
status = client.lock()

# free lock
client.free_lock()
```
