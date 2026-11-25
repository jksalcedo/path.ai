import json

import pytest

from app.controller.pathai_controller import PathAIController
from app.model.dataset_repository import DatasetRepository


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("requested_step", "expected_step"),
    [(0, 1), (1, 1), (2, 2), (3, 3), (4, 3)],
)
async def test_controller_clamps_and_persists_valid_intake_steps(
    storage_backend, requested_step, expected_step
):
    controller = PathAIController(storage_backend)
    await controller.initialize()

    await controller.set_step(requested_step)

    assert controller.answers()["step"] == expected_step
    restored = PathAIController(storage_backend)
    await restored.initialize()
    assert restored.answers()["step"] == expected_step


@pytest.mark.asyncio
async def test_controller_persists_answers_and_submitted_results(storage_backend):
    controller = PathAIController(storage_backend)
    await controller.initialize()

    await controller.set_trait("analytical", 5)
    await controller.set_profile(strand="STEM")
    await controller.set_preferences(prefers_tuition_free=True)
    results = await controller.submit()

    restored = PathAIController(storage_backend)
    await restored.initialize()
    answers = restored.answers()

    assert answers["traits"]["values"]["analytical"] == 5
    assert answers["profile"]["strand"] == "STEM"
    assert answers["preferences"]["prefers_tuition_free"] is True
    assert await restored.last_results() == json.loads(json.dumps(results))


@pytest.mark.asyncio
async def test_controller_uses_skill_answers_when_submitting(storage_backend):
    controller = PathAIController(storage_backend)
    await controller.initialize()
    all_college_ids = [college["id"] for college in controller.college_catalog()]
    for skill in controller.skill_catalog(all_college_ids):
        await controller.set_skill(skill["key"], 5)

    results = await controller.submit()

    assert results
    assert all(result["fit_basis"] == "skills" for result in results)


@pytest.mark.asyncio
async def test_controller_rejects_unknown_skills(storage_backend):
    controller = PathAIController(storage_backend)
    await controller.initialize()

    with pytest.raises(ValueError, match="Unknown skill"):
        await controller.set_skill("not-a-skill", 3)
