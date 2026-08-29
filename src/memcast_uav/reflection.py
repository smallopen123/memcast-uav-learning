from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FlightConstraints:
    min_altitude: float = 0.0
    max_altitude: float = 120.0
    max_speed: float = 8.0
    max_acceleration: float = 1.5
    max_turn_rate: float = 0.20


def _wrap_angle(value: np.ndarray) -> np.ndarray:
    return (value + np.pi) % (2.0 * np.pi) - np.pi


def trajectory_metrics(history: np.ndarray, candidate: np.ndarray, dt: float) -> dict[str, float]:
    history_array = np.asarray(history, dtype=float)
    future_array = np.asarray(candidate, dtype=float)
    if history_array.ndim != 2 or future_array.ndim != 2:
        raise ValueError("history and candidate must be two-dimensional")
    if history_array.shape[1] != 3 or future_array.shape[1] != 3 or len(history_array) < 2:
        raise ValueError("trajectories must contain x, y, z and at least two history points")
    if dt <= 0:
        raise ValueError("dt must be positive")

    joined = np.vstack([history_array[-2:], future_array])
    velocity = np.diff(joined, axis=0) / dt
    speed = np.linalg.norm(velocity, axis=1)
    acceleration = np.diff(velocity, axis=0) / dt
    acceleration_norm = np.linalg.norm(acceleration, axis=1)
    horizontal_speed = np.linalg.norm(velocity[:, :2], axis=1)
    valid_heading = horizontal_speed > 1e-9
    headings = np.arctan2(velocity[:, 1], velocity[:, 0])
    turn_rate = np.abs(_wrap_angle(np.diff(headings))) / dt
    valid_turn = valid_heading[1:] & valid_heading[:-1]
    turn_values = turn_rate[valid_turn]

    return {
        "min_altitude": float(np.min(future_array[:, 2])),
        "max_altitude": float(np.max(future_array[:, 2])),
        "max_speed": float(np.max(speed)),
        "max_acceleration": float(np.max(acceleration_norm)) if acceleration_norm.size else 0.0,
        "max_turn_rate": float(np.max(turn_values)) if turn_values.size else 0.0,
    }


def check_constraints(
    history: np.ndarray,
    candidate: np.ndarray,
    dt: float,
    constraints: FlightConstraints,
    tolerance: float = 1e-6,
) -> list[str]:
    metrics = trajectory_metrics(history, candidate, dt)
    issues: list[str] = []
    if metrics["min_altitude"] < constraints.min_altitude - tolerance:
        issues.append("altitude below minimum")
    if metrics["max_altitude"] > constraints.max_altitude + tolerance:
        issues.append("altitude above maximum")
    if metrics["max_speed"] > constraints.max_speed + tolerance:
        issues.append("speed exceeds limit")
    if metrics["max_acceleration"] > constraints.max_acceleration + tolerance:
        issues.append("acceleration exceeds limit")
    if metrics["max_turn_rate"] > constraints.max_turn_rate + tolerance:
        issues.append("turn rate exceeds limit")
    return issues


def _project_once(
    history: np.ndarray,
    candidate: np.ndarray,
    dt: float,
    constraints: FlightConstraints,
) -> np.ndarray:
    repaired: list[np.ndarray] = []
    previous_point = np.asarray(history[-1], dtype=float).copy()
    previous_velocity = (np.asarray(history[-1]) - np.asarray(history[-2])) / dt

    for desired_point in np.asarray(candidate, dtype=float):
        desired_velocity = (desired_point - previous_point) / dt
        horizontal = desired_velocity[:2]
        horizontal_speed = float(np.linalg.norm(horizontal))
        previous_horizontal = previous_velocity[:2]
        previous_horizontal_speed = float(np.linalg.norm(previous_horizontal))

        if horizontal_speed > 1e-9 and previous_horizontal_speed > 1e-9:
            target_heading = float(np.arctan2(horizontal[1], horizontal[0]))
            previous_heading = float(np.arctan2(previous_horizontal[1], previous_horizontal[0]))
            heading_delta = float(_wrap_angle(np.array([target_heading - previous_heading]))[0])
            maximum_delta = constraints.max_turn_rate * dt
            heading = previous_heading + float(np.clip(heading_delta, -maximum_delta, maximum_delta))
            desired_velocity[:2] = horizontal_speed * np.array([np.cos(heading), np.sin(heading)])

        velocity_change = desired_velocity - previous_velocity
        change_norm = float(np.linalg.norm(velocity_change))
        maximum_change = constraints.max_acceleration * dt
        if change_norm > maximum_change:
            desired_velocity = previous_velocity + velocity_change * (maximum_change / change_norm)

        speed = float(np.linalg.norm(desired_velocity))
        if speed > constraints.max_speed:
            desired_velocity *= constraints.max_speed / speed

        next_point = previous_point + desired_velocity * dt
        next_point[2] = float(
            np.clip(next_point[2], constraints.min_altitude, constraints.max_altitude)
        )
        desired_velocity = (next_point - previous_point) / dt
        repaired.append(next_point)
        previous_point = next_point
        previous_velocity = desired_velocity

    return np.asarray(repaired)


def reflect_candidate(
    history: np.ndarray,
    candidate: np.ndarray,
    dt: float,
    constraints: FlightConstraints,
    max_passes: int = 8,
) -> tuple[np.ndarray, list[dict]]:
    """Deterministically project a trajectory until its kinematics pass the laws."""

    current = np.asarray(candidate, dtype=float).copy()
    trace: list[dict] = []
    for attempt in range(max_passes + 1):
        issues = check_constraints(history, current, dt, constraints)
        trace.append({"attempt": attempt, "issues": issues})
        if not issues:
            return current, trace
        if attempt < max_passes:
            current = _project_once(history, current, dt, constraints)
    raise RuntimeError(f"candidate still violates flight laws: {trace[-1]['issues']}")

