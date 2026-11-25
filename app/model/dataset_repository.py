"""Read-only relational 'database' over the embedded JSON collections."""
import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Dict
from collections import defaultdict
from app.model.entities import HEI, College, Skill, Degree, Offering

class DatasetRepository:
    def __init__(self, data_dir: Optional[str] = None):
        self._dir = Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent / "data"
        self._heis: Dict[str, HEI] = {}
        self._colleges: Dict[str, College] = {}
        self._skills: List[Skill] = []
        self._degrees: Dict[str, Degree] = {}
        self._offerings_by_degree: Dict[str, List[Offering]] = defaultdict(list)
        self._load()

    def _load(self) -> None:
        def read(f): return json.loads((self._dir / f).read_text(encoding="utf-8"))
        
        self._heis = {h["id"]: HEI(**h) for h in read("heis.json")["heis"]}
        self._colleges = {c["id"]: College(**c) for c in read("colleges.json")["colleges"]}
        self._skills = [Skill(**s) for s in read("skills.json")["skills"]]
        self._degrees = {d["id"]: Degree(**d) for d in read("degrees.json")["degrees"]}
        
        for o in read("offerings.json")["offerings"]:
            offering = Offering(**o)
            self._offerings_by_degree[offering.degree_id].append(offering)

    # --- Queries ---
    def heis(self) -> List[HEI]: return list(self._heis.values())
    def hei(self, hei_id: str) -> Optional[HEI]: return self._heis.get(hei_id)
    def locations(self) -> List[str]: return sorted({h.municipality for h in self._heis.values()})
    
    def colleges(self) -> List[College]: return list(self._colleges.values())
    def college(self, college_id: str) -> Optional[College]: return self._colleges.get(college_id)
    
    def skills(self) -> List[Skill]: return list(self._skills)
    def skills_for(self, college_ids) -> List[Skill]:
        ids = set(college_ids)
        return [s for s in self._skills if s.college_id in ids]

    def degrees(self) -> List[Degree]: return list(self._degrees.values())
    
    def offerings_for(self, degree: Degree) -> List[Offering]:
        return self._offerings_by_degree.get(degree.id, [])

    def enrich_offerings(self, offerings: List[Offering]) -> List[dict]:
        """Attaches full HEI details to an offering for the View layer."""
        enriched = []
        for o in offerings:
            h = self.hei(o.hei_id)
            if h:
                enriched.append({
                    "hei": asdict(h),
                    "campus": o.campus or h.municipality
                })
        return enriched