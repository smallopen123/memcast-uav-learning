"""Lesson 04: inspect what one experience-memory entry stores."""

from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.memory import build_memory


def main() -> None:
    flight = make_synthetic_flight()
    train, _ = make_train_test_windows(flight, split_index=504)
    memory = build_memory(train, limit=5)
    entry = memory.entries[0]

    print("课程04：经验记忆")
    print(f"记忆条目数: {len(memory.entries)}")
    print(f"ID: {entry.entry_id}")
    print(f"历史/未来形状: {entry.history.shape} / {entry.future.shape}")
    print(f"意图: {entry.intent}")
    print(f"策略摘要: {entry.strategy}")
    print(f"初始置信度: {entry.confidence}")
    print(f"未来相对位移末点: {entry.future_displacement[-1].round(3).tolist()}")

    # 实践：为 MemoryEntry 增加“环境上下文”字段，例如风速或障碍物密度。


if __name__ == "__main__":
    main()

