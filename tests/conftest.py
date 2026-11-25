import pytest


class InMemoryStorageBackend:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value):
        self.data[key] = value

    async def remove(self, key):
        self.data.pop(key, None)

    async def keys(self, prefix):
        return [key for key in self.data if key.startswith(prefix)]


@pytest.fixture
def storage_backend():
    return InMemoryStorageBackend()
