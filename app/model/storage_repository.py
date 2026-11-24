"""On-device user data. The View team supplies the StorageBackend adapter;
this layer never imports Flet. All values are JSON strings under 'pathai.'."""
from __future__ import annotations

import json
import time
from typing import List, Optional, Protocol

from app.model.entities import IntakeAnswers, Preferences, StudentProfile


class StorageBackend(Protocol):
    async def get(self, key: str) -> Optional[str]: ...
    async def set(self, key: str, value: str) -> None: ...
    async def remove(self, key: str) -> None: ...
    async def keys(self, prefix: str) -> List[str]: ...


class LocalStorageRepository:
    PREFIX = "pathai."
    TTL_SECONDS = 30 * 24 * 60 * 60  # 30-day inactivity purge

    def __init__(self, backend: StorageBackend):
        self._b = backend

    async def touch(self) -> None:
        await self._b.set(self.PREFIX + "last_active", str(int(time.time())))

    async def purge_if_expired(self) -> bool:
        raw = await self._b.get(self.PREFIX + "last_active")
        if raw:
            try:
                if int(time.time()) - int(raw) > self.TTL_SECONDS:
                    await self.clear()
                    return True
            except (TypeError, ValueError):
                await self._b.remove(self.PREFIX + "last_active")
        return False

    async def clear(self) -> None:
        for key in await self._b.keys(self.PREFIX):
            await self._b.remove(key)

    async def has_saved(self) -> bool:
        return await self._b.get(self.PREFIX + "answers") is not None

    async def save_answers(self, answers: IntakeAnswers) -> None:
        await self._b.set(self.PREFIX + "answers", json.dumps(answers.to_dict()))
        await self.touch()

    async def load_answers(self) -> Optional[IntakeAnswers]:
        raw = await self._b.get(self.PREFIX + "answers")
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            await self._b.remove(self.PREFIX + "answers")
            return None
        if not isinstance(data, dict):
            await self._b.remove(self.PREFIX + "answers")
            return None

        preference_data = data.get("preferences", {})
        if isinstance(preference_data, dict):
            preference_data = {
                key: value
                for key, value in preference_data.items()
                if key in Preferences.__dataclass_fields__
            }

        profile_data = data.get("profile", {})
        if isinstance(profile_data, dict):
            profile_data = {
                key: value
                for key, value in profile_data.items()
                if key in StudentProfile.__dataclass_fields__
            }

        data["preferences"] = preference_data
        data["profile"] = profile_data
        return IntakeAnswers.from_dict(data)

    async def save_results(self, payloads: List[dict]) -> None:
        await self._b.set(self.PREFIX + "results", json.dumps(payloads))
        await self.touch()

    async def load_results(self) -> List[dict]:
        raw = await self._b.get(self.PREFIX + "results")
        if not raw:
            return []
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            await self._b.remove(self.PREFIX + "results")
            return []
        return payload if isinstance(payload, list) else []
