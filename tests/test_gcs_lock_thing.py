#!/usr/bin/env python

"""Tests for `gcs_lock_thing` package."""
import unittest

import gcs_lock_thing.lock as gcs
from google.cloud import storage


class TestgcsLockThing(unittest.TestCase):
    """Tests for `gcs_lock_thing` package."""
    public_bucket_path = "data-trf-test-mutex-lock"
    lock_file_name = "test-lock.txt"
    ttl = 2
    client = gcs.Client(bucket=public_bucket_path, lock_file_path=lock_file_name, ttl=ttl)

    def setUp(self):
        """Set up test fixtures, if any."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.public_bucket_path)
        blobs = bucket.list_blobs(prefix='test-lock.txt')
        for blob in blobs:
            blob.delete()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(self.public_bucket_path)
        blobs = bucket.list_blobs(prefix='test-lock.txt')
        for blob in blobs:
            blob.delete()

    def test_basic_lock(self):
        """Test basic use"""
        lock_acquired_status = self.client.lock()
        self.assertTrue(lock_acquired_status)
        free_lock_status = self.client.free_lock()
        self.assertTrue(free_lock_status)

    def test_lock_not_free(self):
        """
        test lock not free
        """
        lock_acquired_status = self.client.lock()
        lock_acquired_status_second_attempt = self.client.lock()
        self.assertTrue(lock_acquired_status)
        self.assertFalse(lock_acquired_status_second_attempt)

    def test_wait_lock_to_free(self):
        self.client.lock()
        lock_acquired_status_second_attempt = self.client.wait_for_lock_expo()
        self.assertTrue(lock_acquired_status_second_attempt)