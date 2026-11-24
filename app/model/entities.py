"""Domain entities for Path.AI (Model layer - no Flet imports).

Three-layer intake:
  Layer 1 -> Preferences (model-adjacent) + StudentProfile (never matched)
  Layer 2 -> TraitProfile   (scores academic clusters)
  Layer 3 -> SkillProfile   (ranks programs within a cluster)
"""
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


# ---------- reference data (read-only, from JSON) ----------

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
    trait_weights: Dict[str, int]      # trait -> 0..3


@dataclass(frozen=True)
class Skill:
    id: str
    college_id: str
    label: str
    hint: str


@dataclass(frozen=True)
class Program:
    id: str
    name: str
    college_id: str
    trait_weights: Dict[str, int]      # trait -> 0..3
    hei_ids: Tuple[str, ...]           # many-to-many junction to HEI
    skill_weights: Dict[str, int] = field(default_factory=dict)   # skill -> 0..3


# ---------- student input ----------

@dataclass
class TraitProfile:
    """Layer 2. Six traits, each 1..5."""
    values: Dict[str, int] = field(default_factory=lambda: {t: 3 for t in TRAIT_KEYS})

    def set(self, key: str, value: int) -> None:
        if key not in TRAIT_KEYS:
            raise ValueError(f"Unknown trait: {key}")
        self.values[key] = max(1, min(5, int(value)))


@dataclass
class SkillProfile:
    """Layer 3. Sparse — only answered skills are stored."""
    values: Dict[str, int] = field(default_factory=dict)

    def set(self, key: str, value: int) -> None:
        self.values[key] = max(1, min(5, int(value)))


@dataclass
class Preferences:
    """Layer 1, model-adjacent only (soft boosts in the engine)."""
    prefers_tuition_free: bool = False
    location: Optional[str] = None
    willing_to_relocate: bool = False
    scholarship_need: bool = False


@dataclass
class StudentProfile:
    """Layer 1, optional context. NEVER passed to the matching engine."""
    strand: Optional[str] = None
    grade_band: Optional[str] = None
    gender: Optional[str] = None


@dataclass
class IntakeAnswers:
    preferences: Preferences = field(default_factory=Preferences)     # Layer 1
    profile: StudentProfile = field(default_factory=StudentProfile)   # Layer 1
    traits: TraitProfile = field(default_factory=TraitProfile)        # Layer 2
    skills: SkillProfile = field(default_factory=SkillProfile)        # Layer 3
    step: int = 1

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "IntakeAnswers":
        traits = TraitProfile()
        traits.values.update(d.get("traits", {}).get("values", {}))
        # filter unknown keys so pre-migration saves (e.g. budget_cap) load safely
        prefs = {k: v for k, v in d.get("preferences", {}).items()
                 if k in Preferences.__dataclass_fields__}
        prof = {k: v for k, v in d.get("profile", {}).items()
                if k in StudentProfile.__dataclass_fields__}
        return cls(
            preferences=Preferences(**prefs),
            profile=StudentProfile(**prof),
            traits=traits,
            skills=SkillProfile(dict(d.get("skills", {}).get("values", {}))),
            step=d.get("step", 1),
        )


# ---------- output ----------

@dataclass
class Recommendation:
    program: Program
    college: College
    match_pct: int
    rank_score: float
    badges: List[str]
    rationale: str
    heis: List[HEI]
    fit_basis: str = "traits"          # "skills" | "traits"; default keeps older call sites valid

    def payload(self) -> dict:
        """JSON-safe, view-ready dict (also what gets persisted)."""
        return asdict(self)