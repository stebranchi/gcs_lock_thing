"""
Try and create lock based off algorithm described here
https://www.joyfulbikeshedding.com/blog/2021-05-19-robust-distributed-locking-algorithm-based-on-google-cloud-storage.html
"""
from datetime import datetime, timedelta

import backoff
import uuid

# Imports the Google Cloud client library
from google.cloud import storage
from google.api_core.exceptions import PreconditionFailed


class Client:
    storage_client = storage.Client()

    def __init__(self, bucket, lock_file_path: str = "gcs_lock_thing.txt", ttl=30, lock_id_prefix='default'):
        self.bucket = bucket
        self.lock_file_path = lock_file_path
        self.ttl = ttl
        self.bucket = self.storage_client.get_bucket(bucket)
        self.lock_file_path = lock_file_path
        self.blob = self.bucket.blob(lock_file_path)
        self.lock_id_prefix = lock_id_prefix
        self.lock_id = f"{lock_id_prefix}-{uuid.uuid4()}"

    def lock(self):
        """
        Creates a lock with the specified GCS path.
        :param lock_path: the lock's GCS path with the gs://bucket-name/file-name format
        :return: boolean, if lock acquired or not
        """

        print(f"Acquiring lock: {self.lock_file_path}")

        try:
            self._upload_lock_file()
            print("Lock acquired: {}".format(self.lock_file_path))
            return True
        except PreconditionFailed:  # this means lock already exists
            print(f"lock as its already in use, checking expiration: {self.lock_file_path}")
            # check if lock is expired
            blob_metadata = self.bucket.get_blob(self.lock_file_path).metadata
            expiration_timestamp = datetime.fromisoformat(blob_metadata.get('expiration_timestamp'))

            if expiration_timestamp < datetime.utcnow():  # lock is stale so we bin it
                self.free_lock()
                self.lock()
                return True

            print("lock is not stale so we wait....")
            return False

    def free_lock(self):
        """
        Free lock
        """
        self.bucket.blob(self.lock_file_path).delete()
        print(f"Lock released: {self.lock_file_path}")
        return True

    def wait_for_lock(self, *backoff_args, **backoff_kwargs):
        """

        """

        @backoff.on_predicate(*backoff_args, **backoff_kwargs)
        def backoff_lock():
            print(f"Backing off lock release: {self.lock_file_path}")
            return self.lock()

        return backoff_lock()

    def wait_for_lock_expo(self, base=2, factor=0.5, max_value=10, max_time=60, jitter=backoff.full_jitter, *args,
                           **kwargs):
        """
        A helper function for `wait_for_lock` that uses exponential backoff.
        :param base: waiting time (sec) is: factor * (base ** n)
        :param factor: waiting time (sec) is: factor * (base ** n)
        :param max_value: the ceiling value for retry time, in seconds
        :param max_time: total retry timeout, in seconds
        :param jitter: See backoff.on_predicate for details. Pass jitter=None for no jitter.
        :return: If the lock was acquired or not
        """
        return self.wait_for_lock(wait_gen=backoff.expo, base=base, factor=factor, max_value=max_value,
                                  max_time=max_time, jitter=jitter, *args, **kwargs)

    def _upload_lock_file(self):
        """
        Upload dummy lock file with id and ttl metadata
        """
        file = 'lock.txt'
        open(file, 'a').close()
        self.blob.upload_from_filename(file, if_generation_match=0)
        metadata = {'expiration_timestamp': datetime.utcnow() + timedelta(seconds=self.ttl),
                    'lock_id': self.lock_id
                    }
        self.blob.metadata = metadata
        self.blob.patch()
