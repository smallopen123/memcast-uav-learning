from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np

from .confidence import (
    CausalConfidenceQueue,
    FeedbackEvent,
    compare_with_baseline,
    constant_velocity_forecast,
    mse,
)
from .data import TrajectoryWindow, make_synthetic_flight, make_train_test_windows
from .features import extract_motion_features
from .memory import ExperienceMemory, build_memory
from .reflection import FlightConstraints, reflect_candidate
from .retrieval import RetrievalConfig, RetrievalResult, retrieve


@dataclass(frozen=True)
class PredictionResult:
    prediction: np.ndarray
    selected_source: str
    contributing_ids: list[str]
    retrieval: list[RetrievalResult]
    candidate_trace: list[dict]


@dataclass(frozen=True)
class DemoResult:
    samples: int
    mse: float
    baseline_mse: float
    memory_entries: int
    accepted_candidates: int
    rejected_candidates: int

    def to_dict(self) -> dict:
        return {
            "samples": self.samples,
            "mse": self.mse,
            "baseline_mse": self.baseline_mse,
            "memory_entries": self.memory_entries,
            "accepted_candidates": self.accepted_candidates,
            "rejected_candidates": self.rejected_candidates,
        }


def _candidate_from_memory(window: TrajectoryWindow, item: RetrievalResult) -> np.ndarray:
    return window.history[-1] + item.entry.future_displacement


def predict_window(
    window: TrajectoryWindow,
    memory: ExperienceMemory,
    retrieval_config: RetrievalConfig,
    constraints: FlightConstraints,
) -> PredictionResult:
    features = extract_motion_features(window.history, window.dt)
    retrieved = retrieve(window.history, features, window.intent, memory, retrieval_config)
    if not retrieved:
        raise RuntimeError("memory is empty")

    raw_candidates: list[tuple[str, np.ndarray, float, list[str]]] = []
    for item in retrieved:
        raw_candidates.append(
            (
                item.entry.entry_id,
                _candidate_from_memory(window, item),
                item.final_score,
                [item.entry.entry_id],
            )
        )
    raw_candidates.append(
        (
            "constant_velocity",
            constant_velocity_forecast(window.history, len(window.future), window.dt),
            retrieved[-1].final_score - 0.05,
            [item.entry.entry_id for item in retrieved],
        )
    )

    valid: list[tuple[str, np.ndarray, float, list[str]]] = []
    candidate_trace: list[dict] = []
    for source, raw, score, contributing_ids in raw_candidates:
        try:
            repaired, reflection_trace = reflect_candidate(
                window.history,
                raw,
                window.dt,
                constraints,
            )
            valid.append((source, repaired, score, contributing_ids))
            candidate_trace.append(
                {"source": source, "status": "accepted", "reflection": reflection_trace}
            )
        except RuntimeError as exc:
            candidate_trace.append(
                {"source": source, "status": "rejected", "reason": str(exc)}
            )

    if not valid:
        raise RuntimeError("all candidate trajectories were rejected")
    selected = max(valid, key=lambda item: item[2])
    return PredictionResult(
        prediction=selected[1],
        selected_source=selected[0],
        contributing_ids=selected[3],
        retrieval=retrieved,
        candidate_trace=candidate_trace,
    )


def run_demo(test_limit: int = 10) -> DemoResult:
    sequence = make_synthetic_flight()
    train_windows, test_windows = make_train_test_windows(sequence, split_index=504)
    memory = build_memory(train_windows, limit=30)
    retrieval_config = RetrievalConfig(alpha=0.5, gamma=120.0, top_k=3, intent_weight=0.25)
    constraints = FlightConstraints()
    queue = CausalConfidenceQueue()
    prediction_errors: list[float] = []
    baseline_errors: list[float] = []
    accepted = 0
    rejected = 0

    for window in test_windows[:test_limit]:
        queue.apply_available(window.forecast_start, memory)
        result = predict_window(window, memory, retrieval_config, constraints)
        feedback = compare_with_baseline(
            window.history,
            result.prediction,
            window.future,
            window.dt,
        )
        queue.add(
            FeedbackEvent(
                event_id=f"test-{window.sample_id}",
                available_at=window.forecast_end,
                contributing_ids=result.contributing_ids,
                feedback=feedback,
            )
        )
        prediction_errors.append(mse(result.prediction, window.future))
        baseline = constant_velocity_forecast(window.history, len(window.future), window.dt)
        baseline_errors.append(mse(baseline, window.future))
        accepted += sum(item["status"] == "accepted" for item in result.candidate_trace)
        rejected += sum(item["status"] == "rejected" for item in result.candidate_trace)

    queue.apply_available(len(sequence.positions), memory)
    return DemoResult(
        samples=len(prediction_errors),
        mse=float(np.mean(prediction_errors)),
        baseline_mse=float(np.mean(baseline_errors)),
        memory_entries=len(memory.entries),
        accepted_candidates=accepted,
        rejected_candidates=rejected,
    )


def main() -> None:
    print(json.dumps(run_demo().to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
