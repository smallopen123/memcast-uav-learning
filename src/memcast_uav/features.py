from __future__ import annotations

import numpy as np

FEATURE_NAMES = (
    "mean_speed",
    "speed_std",
    "max_speed",
    "mean_acceleration",
    "acceleration_std",
    "mean_climb_rate",
    "mean_turn_rate",
    "horizontal_displacement",
    "altitude_change",
)


def _wrap_angle(angle: np.ndarray) -> np.ndarray:
    return (angle + np.pi) % (2.0 * np.pi) - np.pi


def extract_motion_features(history: np.ndarray, dt: float = 1.0) -> np.ndarray:
    """Convert a [history, 3] position trajectory into nine kinematic features."""

    positions = np.asarray(history, dtype=float)
    if positions.ndim != 2 or positions.shape[1] != 3 or len(positions) < 3:
        raise ValueError("history must have shape [time>=3, 3]")
    if dt <= 0:
        raise ValueError("dt must be positive")

    velocity = np.diff(positions, axis=0) / dt
    speed = np.linalg.norm(velocity, axis=1)
    acceleration = np.diff(velocity, axis=0) / dt
    acceleration_norm = np.linalg.norm(acceleration, axis=1)
    heading = np.unwrap(np.arctan2(velocity[:, 1], velocity[:, 0]))
    turn_rate = _wrap_angle(np.diff(heading)) / dt
    displacement = positions[-1] - positions[0]

    return np.array(
        [
            np.mean(speed),
            np.std(speed),
            np.max(speed),
            np.mean(acceleration_norm),
            np.std(acceleration_norm),
            np.mean(velocity[:, 2]),
            np.mean(turn_rate) if turn_rate.size else 0.0,
            np.linalg.norm(displacement[:2]),
            displacement[2],
        ],
        dtype=float,
    )


def translation_invariant_path(history: np.ndarray) -> np.ndarray:
    positions = np.asarray(history, dtype=float)
    if positions.ndim != 2 or positions.shape[1] != 3 or len(positions) == 0:
        raise ValueError("history must have shape [time, 3]")
    return positions - positions[0]
