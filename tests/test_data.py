import numpy as np

from memcast_uav.data import make_synthetic_flight, make_train_test_windows


def test_chronological_split_has_no_target_leakage() -> None:
    sequence = make_synthetic_flight(n_points=360)
    train, test = make_train_test_windows(sequence, split_index=252)
    assert train
    assert test
    assert all(window.forecast_end <= 252 for window in train)
    assert all(window.forecast_start >= 252 for window in test)
    assert test[0].history.shape == (24, 3)
    assert test[0].future.shape == (12, 3)
    assert np.isfinite(test[0].future).all()


def test_synthetic_flight_is_reproducible() -> None:
    first = make_synthetic_flight(n_points=200, seed=17)
    second = make_synthetic_flight(n_points=200, seed=17)
    assert np.array_equal(first.positions, second.positions)
    assert first.intents == second.intents

