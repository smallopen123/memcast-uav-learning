"""Lesson 02: convert a 3-D trajectory into interpretable motion features."""

from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.features import FEATURE_NAMES, extract_motion_features


def main() -> None:
    flight = make_synthetic_flight(n_points=360)
    _, test = make_train_test_windows(flight, split_index=252)
    window = test[0]
    features = extract_motion_features(window.history, window.dt)

    print("课程02：无人机运动学特征")
    for name, value in zip(FEATURE_NAMES, features, strict=True):
        print(f"{name:>24}: {value:9.4f}")
    print(f"特征向量形状: {features.shape}")

    # 实践：加入“历史末端速度”和“距地高度”，思考它们是否需要归一化。


if __name__ == "__main__":
    main()

