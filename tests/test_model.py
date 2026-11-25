import pytest

from app.model.dataset_repository import DatasetRepository
from app.model.entities import Preferences, SkillProfile, TRAIT_KEYS, TraitProfile
from app.model.matching_engine import RuleBasedEngine


def test_dataset_program_references_resolve():
    dataset = DatasetRepository()
    college_ids = {college.id for college in dataset.colleges()}
    hei_ids = {hei.id for hei in dataset.heis()}

    assert dataset.programs()
    assert all(program.college_id in college_ids for program in dataset.programs())
    assert all(
        set(program.hei_ids) <= hei_ids for program in dataset.programs()
    )


def test_recommendations_are_ranked_and_limited_to_program_offerings():
    dataset = DatasetRepository()
    engine = RuleBasedEngine(dataset)

    recommendations = engine.recommend(
        TraitProfile(), Preferences(), top_n=5
    )

    assert len(recommendations) == 5
    assert [item.rank_score for item in recommendations] == sorted(
        (item.rank_score for item in recommendations), reverse=True
    )
    assert all(item.heis for item in recommendations)
    assert all(
        item.program.college_id == item.college.id for item in recommendations
    )


def test_recommendations_use_answered_skills_when_available():
    dataset = DatasetRepository()
    engine = RuleBasedEngine(dataset)
    skills = SkillProfile(
        {skill.id: 5 for skill in dataset.skills()}
    )

    recommendations = engine.recommend(
        TraitProfile(), Preferences(), skills=skills, top_n=5
    )

    assert recommendations
    assert all(item.fit_basis == "skills" for item in recommendations)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, 1), (3, 3), (6, 5)],
)
def test_trait_values_are_clamped(value, expected):
    profile = TraitProfile()

    profile.set(TRAIT_KEYS[0], value)

    assert profile.values[TRAIT_KEYS[0]] == expected


def test_trait_profile_rejects_unknown_traits():
    with pytest.raises(ValueError, match="Unknown trait"):
        TraitProfile().set("unknown", 3)
