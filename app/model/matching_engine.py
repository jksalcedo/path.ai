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
    def _fit(values: dict, weights: dict) -> float:
        return sum(values.get(k, 3) * w for k, w in weights.items()) / (5 * (sum(weights.values()) or 1))

    @staticmethod
    def _rationale(traits: TraitProfile, weights: dict) -> str:
        ranked = sorted(weights, key=weights.get, reverse=True)
        strong = [t for t in ranked if traits.values.get(t, 3) >= 4][:2]
        labels = " and ".join(TRAIT_INFO[t][0].lower() for t in (strong or ranked[:2]))
        return f"Your {labels} interests line up with the core demands of this program."

    def recommend(self, traits, prefs, skills=None, top_n=3, college_k=3):
        ranked = sorted(self._ds.colleges(),
                        key=lambda c: self._fit(traits.values, c.trait_weights), reverse=True)[:college_k]
        cfit = {c.id: self._fit(traits.values, c.trait_weights) for c in ranked}
        results = []
        for p in self._ds.programs():
            if p.college_id not in cfit:            # Stage A gate
                continue
            offering = self._ds.heis_for(p)
            if not offering:
                continue
            sw = p.skill_weights
            if skills and sw and any(k in skills.values for k in sw):
                prog_fit, basis = self._fit(skills.values, sw), "skills"
            else:
                prog_fit, basis = self._fit(traits.values, p.trait_weights), "traits"
            base = 0.4 * cfit[p.college_id] + 0.6 * prog_fit
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
                program=p, college=self._ds.college(p.college_id), match_pct=round(base * 100), rank_score=min(base + bonus, 1.0),
                fit_basis=basis, badges=badges, rationale=self._rationale(traits, p.trait_weights), heis=offering,
            ))
        results.sort(key=lambda r: r.rank_score, reverse=True)
        return results[:top_n]