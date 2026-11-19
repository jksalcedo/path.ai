"""PathAIController — the internal API the Flet View layer calls.
In-process, offline, no HTTP"""
from __future__ import annotations

from typing import List, Optional

from app.model.dataset_repository import DatasetRepository
from app.model.entities import TRAIT_INFO, IntakeAnswers
from app.model.matching_engine import MatchingEngine, RuleBasedEngine
from app.model.storage_repository import LocalStorageRepository, StorageBackend


class PathAIController:
    def __init__(self, storage_backend: StorageBackend, data_dir: Optional[str] = None):
        self._storage = LocalStorageRepository(storage_backend)
        self._dataset = DatasetRepository(data_dir)
        self._engine: MatchingEngine = RuleBasedEngine(self._dataset)
        self.auto_purged = False
        self._answers = IntakeAnswers()

    async def initialize(self) -> None:
        self.auto_purged = await self._storage.purge_if_expired()
        self._answers = await self._storage.load_answers() or IntakeAnswers()
        await self._storage.touch()

    # queries
    def trait_catalog(self) -> List[dict]:
        return [{"key": k, "label": l, "hint": h} for k, (l, h) in TRAIT_INFO.items()]

    def locations(self) -> List[str]:
        return self._dataset.locations()

    async def has_saved(self) -> bool:
        return await self._storage.has_saved()

    def answers(self) -> dict:
        return self._answers.to_dict()

    async def last_results(self) -> List[dict]:
        return await self._storage.load_results()

    # commands (each persists immediately)
    async def set_trait(self, key: str, value: int) -> None:
        self._answers.traits.set(key, value)
        await self._persist()

    async def set_preferences(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if not hasattr(self._answers.preferences, k):
                raise ValueError(f"Unknown preference: {k}")
            if k in ("prefers_tuition_free", "willing_to_relocate", "scholarship_need"):
                v = bool(v)
            if k == "budget_cap":
                v = None if v is None else int(v)
            if k == "location" and not v:
                v = None
            setattr(self._answers.preferences, k, v)
        await self._persist()

    async def set_profile(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if not hasattr(self._answers.profile, k):
                raise ValueError(f"Unknown profile field: {k}")
            setattr(self._answers.profile, k, v or None)
        await self._persist()

    async def set_step(self, step: int) -> None:
        self._answers.step = max(1, min(2, int(step)))
        await self._persist()

    async def submit(self) -> List[dict]:
        # Privacy by construction: only traits + preferences reach the engine.
        recs = self._engine.recommend(self._answers.traits, self._answers.preferences)
        payloads = [r.payload() for r in recs]
        await self._storage.save_results(payloads)
        await self._persist()
        return payloads

    async def clear_my_data(self) -> None:
        await self._storage.clear()
        self._answers = IntakeAnswers()

    async def _persist(self) -> None:
        await self._storage.save_answers(self._answers)
