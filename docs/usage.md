# Usage

To use gcs-lock-thing in a project:

```python
import gcs_lock_thing.lock as gcs

public_bucket_path = "data-trf-test-mutex-lock"
lock_file_name = "test-lock.txt"
ttl = 2
client = gcs.Client(bucket=public_bucket_path, lock_file_path=lock_file_name, ttl=ttl)

# get lock
status = client.lock()

# free lock
client.free_lock()
```


