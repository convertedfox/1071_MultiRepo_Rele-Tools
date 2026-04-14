from __future__ import annotations

from dashboard.state import (
    KEY_STEP_1049_DONE,
    KEY_STEP_1052_DONE,
    KEY_STEP_1067_DONE,
    WorkflowStep,
    init_state,
    is_step_completed,
    mark_step_completed,
)


def test_init_state_sets_defaults() -> None:
    store: dict[str, object] = {}

    init_state(store)

    assert store[KEY_STEP_1049_DONE] is False
    assert store[KEY_STEP_1067_DONE] is False
    assert store[KEY_STEP_1052_DONE] is False


def test_init_state_preserves_existing_values() -> None:
    store: dict[str, object] = {KEY_STEP_1049_DONE: True}

    init_state(store)

    assert store[KEY_STEP_1049_DONE] is True


def test_mark_step_completed() -> None:
    store: dict[str, object] = {}
    init_state(store)

    mark_step_completed(store, WorkflowStep.RELE_1067)

    assert is_step_completed(store, WorkflowStep.RELE_1067) is True
    assert is_step_completed(store, WorkflowStep.PDF_1049) is False
