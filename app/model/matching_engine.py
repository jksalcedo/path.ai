"""Strategy interface + rule-based implementation.
Add JsonDecisionTreeEngine(MatchingEngine) loading an exported model_rules.json file."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.model.dataset_repository import DatasetRepository
from app.model.entities import TRAIT_INFO, Preferences, Recommendation, TraitProfile


class MatchingEngine(ABC):
    @abstractmethod
    def recommend(self, traits: TraitProfile, prefs: Preferences, top_n: int = 3) -> List[Recommendation]: ...


class RuleBasedEngine(MatchingEngine):
    def __init__(self, dataset: DatasetRepository):
        self._ds = dataset

    @staticmethod
    def _fit(traits: TraitProfile, weights: dict) -> float:
        total = sum(weights.values()) or 1
        return sum(traits.values.get(t, 3) * w for t, w in weights.items()) / (5 * total)

    @staticmethod
    def _rationale(traits: TraitProfile, weights: dict) -> str:
        ranked = sorted(weights, key=weights.get, reverse=True)
        strong = [t for t in ranked if traits.values.get(t, 3) >= 4][:2]
        labels = " and ".join(TRAIT_INFO[t][0].lower() for t in (strong or ranked[:2]))
        return f"Your {labels} interests line up with the core demands of this program."

    def recommend(self, traits: TraitProfile, prefs: Preferences, top_n: int = 3) -> List[Recommendation]:
        results: List[Recommendation] = []
        for p in self._ds.programs():
            offering = self._ds.heis_for(p)
            if not offering:
                continue
            base = self._fit(traits, p.trait_weights)
            bonus, badges = 0.0, []
            if prefs.prefers_tuition_free and any(not h.requires_tuition for h in offering):
                bonus += 0.05
                badges.append("Tuition-free option")
            if prefs.location and any(h.municipality == prefs.location for h in offering):
                bonus += 0.05
                badges.append("Preferred location")
            elif prefs.location and not prefs.willing_to_relocate:
                bonus -= 0.03
            if prefs.scholarship_need and any(h.scholarships for h in offering):
                bonus += 0.03
                badges.append("Scholarships available")
            results.append(Recommendation(
                program=p, match_pct=round(base * 100), rank_score=min(base + bonus, 1.0),
                badges=badges, rationale=self._rationale(traits, p.trait_weights), heis=offering,
            ))
        results.sort(key=lambda r: r.rank_score, reverse=True)
        return results[:top_n]