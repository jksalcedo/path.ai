"""Flet client_storage adapter implementing the Model's StorageBackend protocol."""


class FletStorageAdapter:
    def __init__(self, page):
        self._s = page.client_storage

    def get(self, key):
        return self._s.get(key)

    def set(self, key, value):
        self._s.set(key, value)

    def remove(self, key):
        self._s.remove(key)

    def keys(self, prefix):
        return self._s.get_keys(prefix)