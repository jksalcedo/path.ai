"""On-device user data. The View team supplies the StorageBackend adapter;
this layer never imports Flet. All values are JSON strings under 'pathai.'."""
from __future__ import annotations

import json
import time
from typing import List, Optional, Protocol

from app.model.entities import IntakeAnswers


class StorageBackend(Protocol):
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str) -> None: ...
    def remove(self, key: str) -> None: ...
    def keys(self, prefix: str) -> List[str]: ...


class LocalStorageRepository:
    PREFIX = "pathai."
    TTL_SECONDS = 30 * 24 * 60 * 60  # 30-day inactivity purge

    def __init__(self, backend: StorageBackend):
        self._b = backend

    def touch(self) -> None:
        self._b.set(self.PREFIX + "last_active", str(int(time.time())))

    def purge_if_expired(self) -> bool:
        raw = self._b.get(self.PREFIX + "last_active")
        if raw and int(time.time()) - int(raw) > self.TTL_SECONDS:
            self.clear()
            return True
        return False

    def clear(self) -> None:
        for key in self._b.keys(self.PREFIX):
            self._b.remove(key)

    def has_saved(self) -> bool:
        return self._b.get(self.PREFIX + "answers") is not None

    def save_answers(self, answers: IntakeAnswers) -> None:
        self._b.set(self.PREFIX + "answers", json.dumps(answers.to_dict()))
        self.touch()

    def load_answers(self) -> Optional[IntakeAnswers]:
        raw = self._b.get(self.PREFIX + "answers")
        return IntakeAnswers.from_dict(json.loads(raw)) if raw else None

    def save_results(self, payloads: List[dict]) -> None:
        self._b.set(self.PREFIX + "results", json.dumps(payloads))
        self.touch()

    def load_results(self) -> List[dict]:
        raw = self._b.get(self.PREFIX + "results")
        return json.loads(raw) if raw else []