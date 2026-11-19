"""Read-only 'database' over the embedded JSON collections."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from app.model.entities import HEI, Program


class DatasetRepository:
    def __init__(self, data_dir: Optional[str] = None):
        self._dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "data"
        self._heis = {}
        self._programs: List[Program] = []
        self._load()

    def _load(self) -> None:
        raw_h = json.loads((self._dir / "heis.json").read_text(encoding="utf-8"))["heis"]
        raw_p = json.loads((self._dir / "programs.json").read_text(encoding="utf-8"))["programs"]
        self._heis = {h["id"]: HEI(**h) for h in raw_h}
        self._programs = [
            Program(id=p["id"], name=p["name"],
                    trait_weights=p["trait_weights"], hei_ids=tuple(p["hei_ids"]))
            for p in raw_p
        ]

    def heis(self) -> List[HEI]:
        return list(self._heis.values())

    def programs(self) -> List[Program]:
        return list(self._programs)

    def hei(self, hei_id: str) -> Optional[HEI]:
        return self._heis.get(hei_id)

    def heis_for(self, program: Program) -> List[HEI]:
        return [self._heis[i] for i in program.hei_ids if i in self._heis]

    def locations(self) -> List[str]:
        return sorted({h.municipality for h in self._heis.values()})
        