import numpy as np

from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.reflection import FlightConstraints, check_constraints, reflect_candidate


def test_reflection_repairs_extreme_candidate() -> None:
    sequence = make_synthetic_flight(n_points=360)
    _, test = make_train_test_windows(sequence, split_index=252)
    window = test[0]
    candidate = window.future.copy()
    candidate[:, 0] += np.linspace(0.0, 300.0, len(candidate))
    candidate[:, 2] = np.linspace(window.history[-1, 2], 180.0, len(candidate))
    constraints = FlightConstraints()
    assert check_constraints(window.history, candidate, window.dt, constraints)
    repaired, trace = reflect_candidate(window.history, candidate, window.dt, constraints)
    assert len(trace) >= 2
    assert not check_constraints(window.history, repaired, window.dt, constraints)

