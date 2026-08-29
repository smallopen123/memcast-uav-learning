"""Lesson 08: observe how an externally supplied intent changes retrieval."""

from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.features import extract_motion_features
from memcast_uav.memory import build_memory
from memcast_uav.retrieval import RetrievalConfig, retrieve


def _top_intents(intent_weight: float) -> list[str]:
    flight = make_synthetic_flight()
    train, test = make_train_test_windows(flight, split_index=504)
    memory = build_memory(train, limit=30)
    # Sample 3 is deliberately chosen because shape-only retrieval mixes a
    # left-turn memory into this right-turn query, making the intent effect visible.
    query = test[3]
    ranked = retrieve(
        query.history,
        extract_motion_features(query.history, query.dt),
        query.intent,
        memory,
        RetrievalConfig(
            alpha=0.5,
            gamma=120.0,
            top_k=3,
            intent_weight=intent_weight,
        ),
    )
    return [item.entry.intent for item in ranked]


def main() -> None:
    without_intent = _top_intents(intent_weight=0.0)
    with_intent = _top_intents(intent_weight=0.6)
    print("课程08：意图条件检索")
    print(f"不使用意图时的Top-3: {without_intent}")
    print(f"提高意图权重后的Top-3: {with_intent}")
    print("真实系统中，意图必须来自任务规划、控制指令或在线意图识别器。")
    print("不能读取真实未来轨迹后再反推意图，否则会发生标签泄漏。")

    # 实践：把意图拆成层级标签，例如 mission=delivery, maneuver=turn_left。


if __name__ == "__main__":
    main()
