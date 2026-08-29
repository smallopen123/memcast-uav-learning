"""Lesson 01: understand chronological history/forecast windows."""

from memcast_uav.data import make_synthetic_flight, make_train_test_windows


def main() -> None:
    flight = make_synthetic_flight(n_points=360)
    train, test = make_train_test_windows(
        flight,
        split_index=252,
        history=24,
        horizon=12,
        stride=12,
    )
    first = test[0]
    print("课程01：时间窗口与数据泄漏")
    print(f"完整序列点数: {len(flight.positions)}")
    print(f"训练窗口数: {len(train)}, 测试窗口数: {len(test)}")
    print(
        "第一个测试窗口: "
        f"history=[{first.history_start}:{first.forecast_start}), "
        f"future=[{first.forecast_start}:{first.forecast_end})"
    )
    print(f"历史形状: {first.history.shape}, 未来形状: {first.future.shape}")
    print(f"预测区间意图（假设来自任务规划）: {first.intent}")
    assert train[-1].forecast_end <= 252
    assert first.forecast_start >= 252
    print("检查通过：训练目标没有跨越划分点，测试目标没有进入训练段。")

    # 实践：把 stride 改成 6，观察窗口数量和相邻窗口重叠率如何变化。


if __name__ == "__main__":
    main()

