from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .memory import ExperienceMemory


def mse(prediction: np.ndarray, truth: np.ndarray) -> float:
    predicted = np.asarray(prediction, dtype=float)
    actual = np.asarray(truth, dtype=float)
    if predicted.shape != actual.shape or predicted.size == 0:
        raise ValueError("prediction and truth must have equal non-empty shape")
    return float(np.mean((predicted - actual) ** 2))


def constant_velocity_forecast(history: np.ndarray, horizon: int, dt: float) -> np.ndarray:
    positions = np.asarray(history, dtype=float)
    velocity = (positions[-1] - positions[-2]) / dt
    steps = np.arange(1, horizon + 1, dtype=float)[:, None]
    return positions[-1] + steps * velocity * dt


def compare_with_baseline(
    history: np.ndarray,
    prediction: np.ndarray,
    truth: np.ndarray,
    dt: float,
) -> dict:
    baseline = constant_velocity_forecast(history, len(truth), dt)
    prediction_mse = mse(prediction, truth)
    baseline_mse = mse(baseline, truth)
    return {
        "prediction_mse": prediction_mse,
        "baseline_mse": baseline_mse,
        "success": prediction_mse < baseline_mse,
    }


@dataclass
class FeedbackEvent:
    event_id: str
    available_at: int
    contributing_ids: list[str]
    feedback: dict
    applied: bool = False


class CausalConfidenceQueue:
    """Delay truth-dependent memory updates until the forecast horizon is observable."""

    def __init__(self) -> None:
        self.events: list[FeedbackEvent] = []

    def add(self, event: FeedbackEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self.events):
            raise ValueError(f"duplicate feedback event: {event.event_id}")
        self.events.append(event)

    def apply_available(
        self,
        observation_index: int,
        memory: ExperienceMemory,
        delta: float = 0.01,
    ) -> int:
        updated = 0
        for event in self.events:
            if event.applied or event.available_at > observation_index:
                continue
            if event.feedback.get("success"):
                updated += memory.update_confidence(event.contributing_ids, delta)
            event.applied = True
        return updated

