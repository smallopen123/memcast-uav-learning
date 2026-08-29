"""Lesson 05: repair a candidate that violates UAV flight constraints."""

import numpy as np

from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.reflection import (
    FlightConstraints,
    check_constraints,
    reflect_candidate,
    trajectory_metrics,
)


def main() -> None:
    flight = make_synthetic_flight(n_points=360)
    _, test = make_train_test_windows(flight, split_index=252)
    window = test[0]
    constraints = FlightConstraints(max_speed=8.0, max_acceleration=1.5, max_altitude=120.0)

    # 故意制造瞬间高速上升、超过高度上限的不合法候选。
    candidate = window.future.copy()
    candidate[:, 0] += np.linspace(0.0, 300.0, len(candidate))
    candidate[:, 2] = np.linspace(window.history[-1, 2], 180.0, len(candidate))

    before = check_constraints(window.history, candidate, window.dt, constraints)
    repaired, trace = reflect_candidate(window.history, candidate, window.dt, constraints)
    after = check_constraints(window.history, repaired, window.dt, constraints)

    print("课程05：飞行约束反思")
    print(f"修正前违反: {before}")
    print(f"反思轮数: {len(trace) - 1}")
    print(f"修正后违反: {after}")
    print(f"修正后指标: {trajectory_metrics(window.history, repaired, window.dt)}")
    assert not after

    # 实践：加入禁飞区约束；注意它属于空间几何约束，不只是数值上下界。


if __name__ == "__main__":
    main()

