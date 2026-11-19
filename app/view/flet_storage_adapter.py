"""Flet persistent-storage adapter implementing the model storage protocol."""

import inspect


class FletStorageAdapter:
    def __init__(self, page):
        self._s = getattr(page, "client_storage", None)
        if self._s is None:
            import flet as ft

            self._s = ft.SharedPreferences()

    async def get(self, key):
        value = self._s.get(key)
        return await value if inspect.isawaitable(value) else value

    async def set(self, key, value):
        result = self._s.set(key, value)
        if inspect.isawaitable(result):
            await result

    async def remove(self, key):
        result = self._s.remove(key)
        if inspect.isawaitable(result):
            await result

    async def keys(self, prefix):
        keys = self._s.get_keys(prefix)
        return await keys if inspect.isawaitable(keys) else keys
