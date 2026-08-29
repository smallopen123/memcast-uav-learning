from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

INTENTS = ("cruise", "turn_left", "turn_right", "climb", "descend")


@dataclass(frozen=True)
class FlightSequence:
    """One flight in a local Cartesian ENU-like coordinate system."""

    positions: np.ndarray
    intents: tuple[str, ...]
    dt: float = 1.0

    def __post_init__(self) -> None:
        positions = np.asarray(self.positions, dtype=float)
        if positions.ndim != 2 or positions.shape[1] != 3:
            raise ValueError("positions must have shape [time, 3]")
        if positions.shape[0] != len(self.intents):
            raise ValueError("positions and intents must have equal length")
        if positions.shape[0] < 3 or self.dt <= 0:
            raise ValueError("flight must contain at least three points and use positive dt")
        object.__setattr__(self, "positions", positions)


@dataclass(frozen=True)
class TrajectoryWindow:
    sample_id: int
    history_start: int
    forecast_start: int
    forecast_end: int
    history: np.ndarray
    future: np.ndarray
    intent: str
    dt: float

    def __post_init__(self) -> None:
        history = np.asarray(self.history, dtype=float)
        future = np.asarray(self.future, dtype=float)
        if history.ndim != 2 or future.ndim != 2:
            raise ValueError("history and future must be two-dimensional")
        if history.shape[1:] != (3,) or future.shape[1:] != (3,):
            raise ValueError("trajectory windows must contain x, y, z")
        if self.forecast_start - self.history_start != len(history):
            raise ValueError("window indices do not match history length")
        if self.forecast_end - self.forecast_start != len(future):
            raise ValueError("window indices do not match future length")
        object.__setattr__(self, "history", history)
        object.__setattr__(self, "future", future)


def make_synthetic_flight(n_points: int = 720, seed: int = 7, dt: float = 1.0) -> FlightSequence:
    """Create a deterministic smooth flight with five repeating maneuver intents."""

    if n_points < 160:
        raise ValueError("n_points must be at least 160")
    rng = np.random.default_rng(seed)
    positions = np.zeros((n_points, 3), dtype=float)
    positions[0] = [0.0, 0.0, 35.0]
    intents: list[str] = []
    heading = 0.2
    horizontal_speed = 4.5
    vertical_speed = 0.0

    for index in range(n_points):
        intent = INTENTS[(index // 72) % len(INTENTS)]
        intents.append(intent)
        if index == 0:
            continue

        yaw_rate = 0.0
        target_vertical_speed = 0.0
        if intent == "turn_left":
            yaw_rate = 0.018
        elif intent == "turn_right":
            yaw_rate = -0.018
        elif intent == "climb":
            target_vertical_speed = 0.35
        elif intent == "descend":
            target_vertical_speed = -0.30

        heading += yaw_rate * dt
        vertical_speed += 0.08 * (target_vertical_speed - vertical_speed)
        horizontal_speed += 0.03 * (4.5 - horizontal_speed)
        noise = rng.normal(0.0, [0.025, 0.025, 0.01])
        velocity = np.array(
            [
                horizontal_speed * np.cos(heading),
                horizontal_speed * np.sin(heading),
                vertical_speed,
            ]
        )
        positions[index] = positions[index - 1] + velocity * dt + noise
        positions[index, 2] = max(5.0, positions[index, 2])

    return FlightSequence(positions=positions, intents=tuple(intents), dt=dt)


def _majority_intent(values: Sequence[str]) -> str:
    counts = {value: values.count(value) for value in set(values)}
    return max(counts, key=lambda value: (counts[value], -values.index(value)))


def make_windows(
    sequence: FlightSequence,
    history: int,
    horizon: int,
    stride: int,
    region_start: int = 0,
    region_stop: int | None = None,
) -> list[TrajectoryWindow]:
    """Build windows whose history and future are completely inside one region."""

    if min(history, horizon, stride) <= 0:
        raise ValueError("history, horizon and stride must be positive")
    stop = len(sequence.positions) if region_stop is None else region_stop
    if not 0 <= region_start < stop <= len(sequence.positions):
        raise ValueError("invalid region")

    windows: list[TrajectoryWindow] = []
    for start in range(region_start, stop - history - horizon + 1, stride):
        forecast_start = start + history
        forecast_end = forecast_start + horizon
        future_intents = list(sequence.intents[forecast_start:forecast_end])
        windows.append(
            TrajectoryWindow(
                sample_id=len(windows),
                history_start=start,
                forecast_start=forecast_start,
                forecast_end=forecast_end,
                history=sequence.positions[start:forecast_start].copy(),
                future=sequence.positions[forecast_start:forecast_end].copy(),
                intent=_majority_intent(future_intents),
                dt=sequence.dt,
            )
        )
    return windows


def make_train_test_windows(
    sequence: FlightSequence,
    split_index: int,
    history: int = 24,
    horizon: int = 12,
    stride: int = 12,
) -> tuple[list[TrajectoryWindow], list[TrajectoryWindow]]:
    """Create chronological windows with no future-target overlap across the split."""

    if not history + horizon <= split_index <= len(sequence.positions) - horizon:
        raise ValueError("split_index leaves insufficient train or test data")
    train = make_windows(sequence, history, horizon, stride, 0, split_index)

    # The first test history may use observations immediately before the split,
    # but every test target starts at or after split_index.
    test_start = split_index - history
    test = make_windows(sequence, history, horizon, stride, test_start, len(sequence.positions))
    if any(window.forecast_end > split_index for window in train):
        raise RuntimeError("training target crosses split")
    if any(window.forecast_start < split_index for window in test):
        raise RuntimeError("test target starts before split")
    return train, test
