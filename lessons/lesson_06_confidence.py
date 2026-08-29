"""Lesson 06: update memory confidence only when truth is causally available."""

from memcast_uav.confidence import CausalConfidenceQueue, FeedbackEvent
from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.memory import build_memory


def main() -> None:
    flight = make_synthetic_flight()
    train, test = make_train_test_windows(flight, split_index=504)
    memory = build_memory(train, limit=3)
    entry_id = memory.entries[0].entry_id
    event = FeedbackEvent(
        event_id="example-feedback",
        available_at=test[0].forecast_end,
        contributing_ids=[entry_id],
        feedback={"success": True},
    )
    queue = CausalConfidenceQueue()
    queue.add(event)

    before = memory.get(entry_id).confidence
    early_updates = queue.apply_available(test[0].forecast_start, memory)
    middle = memory.get(entry_id).confidence
    mature_updates = queue.apply_available(test[0].forecast_end, memory)
    after = memory.get(entry_id).confidence

    print("课程06：因果置信度更新")
    print(f"初始置信度: {before:.2f}")
    print(f"未来尚不可见时更新条目数: {early_updates}, confidence={middle:.2f}")
    print(f"预测区间结束后更新条目数: {mature_updates}, confidence={after:.2f}")
    assert before == middle and after > middle

    # 实践：把 feedback.success 改成 False，确认置信度不会增加。


if __name__ == "__main__":
    main()

