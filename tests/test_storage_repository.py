import pytest

from app.model.entities import IntakeAnswers
from app.model.storage_repository import LocalStorageRepository


@pytest.mark.asyncio
async def test_saved_answers_round_trip(storage_backend):
    repository = LocalStorageRepository(storage_backend)
    answers = IntakeAnswers(step=3)
    answers.traits.set("creative", 5)

    await repository.save_answers(answers)
    restored = await repository.load_answers()

    assert restored is not None
    assert restored.step == 3
    assert restored.traits.values["creative"] == 5


@pytest.mark.asyncio
async def test_expired_data_is_cleared_but_unrelated_data_is_preserved(
    storage_backend, monkeypatch
):
    now = 2_000_000_000
    monkeypatch.setattr("app.model.storage_repository.time.time", lambda: now)
    storage_backend.data.update(
        {
            "pathai.last_active": str(now - LocalStorageRepository.TTL_SECONDS - 1),
            "pathai.answers": "{}",
            "another_app.setting": "keep",
        }
    )
    repository = LocalStorageRepository(storage_backend)

    assert await repository.purge_if_expired() is True
    assert storage_backend.data == {"another_app.setting": "keep"}


@pytest.mark.asyncio
async def test_invalid_saved_answers_are_removed(storage_backend):
    storage_backend.data["pathai.answers"] = "{invalid json"
    repository = LocalStorageRepository(storage_backend)

    assert await repository.load_answers() is None
    assert "pathai.answers" not in storage_backend.data
