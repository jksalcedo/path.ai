"""Domain entities for Path.AI (Relational Model)."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

TRAIT_KEYS = ("analytical", "creative", "technical", "people", "organizational", "entrepreneurial")
TRAIT_INFO = {
    "analytical":      ("Analytical", "Logic, numbers, and problem-solving"),
    "creative":        ("Creative", "Design, writing, and original ideas"),
    "technical":       ("Technical", "Computers, tools, and building systems"),
    "people":          ("People-oriented", "Helping, teaching, and teamwork"),
    "organizational":  ("Organizational", "Planning, detail, and order"),
    "entrepreneurial": ("Entrepreneurial", "Business, selling, and leading ventures"),
}

# ---------- reference data ----------

@dataclass(frozen=True)
class HEI:
    id: str
    name: str
    municipality: str
    type: str
    requires_tuition: bool
    scholarships: bool
    tuition_note: str

@dataclass(frozen=True)
class College:
    id: str
    name: str
    trait_weights: Dict[str, int]

@dataclass(frozen=True)
class Skill:
    id: str
    college_id: str
    label: str
    hint: str

@dataclass(frozen=True)
class Degree:
    """The core CHED-standardized program. This is what the ML model predicts."""
    id: str
    name: str
    college_id: str
    trait_weights: Dict[str, int]
    skill_weights: Dict[str, int] = field(default_factory=dict)

@dataclass(frozen=True)
class Offering:
    """Junction table: Maps an HEI to a Degree, with optional campus info."""
    hei_id: str
    degree_id: str
    campus: Optional[str] = None

# ---------- student input ----------

@dataclass
class TraitProfile:
    values: Dict[str, int] = field(default_factory=lambda: {t: 3 for t in TRAIT_KEYS})
    def set(self, key: str, value: int) -> None:
        if key not in TRAIT_KEYS: raise ValueError(f"Unknown trait: {key}")
        self.values[key] = max(1, min(5, int(value)))

@dataclass
class SkillProfile:
    values: Dict[str, int] = field(default_factory=dict)
    def set(self, key: str, value: int) -> None:
        self.values[key] = max(1, min(5, int(value)))

@dataclass
class Preferences:
    prefers_tuition_free: bool = False
    location: Optional[str] = None
    willing_to_relocate: bool = False
    scholarship_need: bool = False

@dataclass
class StudentProfile:
    strand: Optional[str] = None
    grade_band: Optional[str] = None
    gender: Optional[str] = None

@dataclass
class IntakeAnswers:
    preferences: Preferences = field(default_factory=Preferences)
    profile: StudentProfile = field(default_factory=StudentProfile)
    traits: TraitProfile = field(default_factory=TraitProfile)
    skills: SkillProfile = field(default_factory=SkillProfile)
    step: int = 1

    def to_dict(self) -> dict: return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "IntakeAnswers":
        traits = TraitProfile()
        traits.values.update(d.get("traits", {}).get("values", {}))
        prefs = {k: v for k, v in d.get("preferences", {}).items() if k in Preferences.__dataclass_fields__}
        prof = {k: v for k, v in d.get("profile", {}).items() if k in StudentProfile.__dataclass_fields__}
        return cls(
            preferences=Preferences(**prefs), profile=StudentProfile(**prof),
            traits=traits, skills=SkillProfile(dict(d.get("skills", {}).get("values", {}))),
            step=d.get("step", 1),
        )

# ---------- output ----------

@dataclass
class Recommendation:
    degree: Degree
    college: College
    match_pct: int
    rank_score: float
    badges: List[str]
    rationale: str
    offerings: List[dict]  # Enriched with HEI details + campus
    fit_basis: str = "traits"

    def payload(self) -> dict: return asdict(self)