"""Domain entities for Path.AI (Model layer)

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


@dataclass(frozen=True)
class HEI:
    id: str
    name: str
    municipality: str
    type: str
    est_annual_tuition_php: int
    scholarships: bool
    tuition_note: str


@dataclass(frozen=True)
class Program:
    id: str
    name: str
    trait_weights: Dict[str, int]   # trait -> 0..3
    hei_ids: Tuple[str, ...]        # many-to-many junction to HEI


@dataclass
class TraitProfile:
    values: Dict[str, int] = field(default_factory=lambda: {t: 3 for t in TRAIT_KEYS})

    def set(self, key: str, value: int) -> None:
        if key not in TRAIT_KEYS:
            raise ValueError(f"Unknown trait: {key}")
        self.values[key] = max(1, min(5, int(value)))


@dataclass
class Preferences:
    """Model-adjacent preferences only (soft boosts in the engine)."""
    budget_cap: Optional[int] = None
    location: Optional[str] = None
    willing_to_relocate: bool = False
    scholarship_need: bool = False


@dataclass
class StudentProfile:
    """Optional context. NEVER passed to the matching engine (privacy rule)."""
    strand: Optional[str] = None
    grade_band: Optional[str] = None
    gender: Optional[str] = None


@dataclass
class IntakeAnswers:
    traits: TraitProfile = field(default_factory=TraitProfile)
    preferences: Preferences = field(default_factory=Preferences)
    profile: StudentProfile = field(default_factory=StudentProfile)
    step: int = 1

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "IntakeAnswers":
        traits = TraitProfile()
        traits.values.update(d.get("traits", {}).get("values", {}))
        return cls(
            traits=traits,
            preferences=Preferences(**d.get("preferences", {})),
            profile=StudentProfile(**d.get("profile", {})),
            step=d.get("step", 1),
        )


@dataclass
class Recommendation:
    program: Program
    match_pct: int
    rank_score: float
    badges: List[str]
    rationale: str
    heis: List[HEI]

    def payload(self) -> dict:
        """JSON-safe, view-ready dict (also what gets persisted)."""
        return asdict(self)