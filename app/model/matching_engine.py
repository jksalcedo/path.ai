"""Two-stage hierarchical matching engine."""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.model.dataset_repository import DatasetRepository
from app.model.entities import TRAIT_INFO, Preferences, Recommendation, TraitProfile, SkillProfile, Degree

class MatchingEngine(ABC):
    @abstractmethod
    def recommend(self, traits: TraitProfile, prefs: Preferences, skills: Optional[SkillProfile] = None, top_n: int = 3) -> List[Recommendation]: ...

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
        return f"Your {labels} interests line up with the core demands of this field."

    def recommend(self, traits: TraitProfile, prefs: Preferences, skills: Optional[SkillProfile] = None, top_n: int = 3) -> List[Recommendation]:
        # Stage A: Rank Colleges (Clusters)
        ranked_cols = sorted(self._ds.colleges(), key=lambda c: self._fit(traits.values, c.trait_weights), reverse=True)
        top_col_ids = {c.id for c in ranked_cols[:3]}
        cfit = {c.id: self._fit(traits.values, c.trait_weights) for c in ranked_cols}

        results: List[Recommendation] = []
        
        # Stage B: Rank Degrees within top colleges
        for d in self._ds.degrees():
            if d.college_id not in top_col_ids: continue  # Hard gate
            
            offerings = self._ds.offerings_for(d)
            if not offerings: continue
            
            offering_heis = [self._ds.hei(o.hei_id) for o in offerings if self._ds.hei(o.hei_id)]
            if not offering_heis: continue

            # Calculate program fit (skills if available, else traits)
            sw = d.skill_weights
            if skills and sw and any(k in skills.values for k in sw):
                prog_fit, basis = self._fit(skills.values, sw), "skills"
            else:
                prog_fit, basis = self._fit(traits.values, d.trait_weights), "traits"
                
            base = 0.4 * cfit[d.college_id] + 0.6 * prog_fit
            
            # Apply preference bonuses based on the HEIs that offer this degree
            bonus, badges = 0.0, []
            if prefs.prefers_tuition_free and any(not h.requires_tuition for h in offering_heis):
                bonus += 0.05; badges.append("Tuition-free option")
            if prefs.location and any(h.municipality == prefs.location for h in offering_heis):
                bonus += 0.05; badges.append("Preferred location")
            elif prefs.location and not prefs.willing_to_relocate:
                bonus -= 0.03
            if prefs.scholarship_need and any(h.scholarships for h in offering_heis):
                bonus += 0.03; badges.append("Scholarships available")

            results.append(Recommendation(
                degree=d, college=self._ds.college(d.college_id), match_pct=round(base * 100),
                rank_score=min(base + bonus, 1.0), fit_basis=basis, badges=badges,
                rationale=self._rationale(traits, d.trait_weights), 
                offerings=self._ds.enrich_offerings(offerings)
            ))
            
        results.sort(key=lambda r: r.rank_score, reverse=True)
        return results[:top_n]