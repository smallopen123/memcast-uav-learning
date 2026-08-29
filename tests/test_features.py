import numpy as np

from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.features import FEATURE_NAMES, extract_motion_features, translation_invariant_path


def test_motion_features_have_named_finite_values() -> None:
    sequence = make_synthetic_flight(n_points=360)
    _, test = make_train_test_windows(sequence, split_index=252)
    features = extract_motion_features(test[0].history, test[0].dt)
    assert features.shape == (len(FEATURE_NAMES),)
    assert np.isfinite(features).all()


def test_relative_path_is_translation_invariant() -> None:
    path = np.array([[1.0, 2.0, 3.0], [2.0, 4.0, 6.0]])
    shifted = path + np.array([100.0, -20.0, 7.0])
    assert np.allclose(translation_invariant_path(path), translation_invariant_path(shifted))

