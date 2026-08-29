"""Lesson 03: retrieve similar maneuvers using features, DTW and intent."""

from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.features import extract_motion_features
from memcast_uav.memory import build_memory
from memcast_uav.retrieval import RetrievalConfig, retrieve


def main() -> None:
    flight = make_synthetic_flight()
    train, test = make_train_test_windows(flight, split_index=504)
    memory = build_memory(train, limit=30)
    query = test[0]
    query_features = extract_motion_features(query.history, query.dt)
    ranked = retrieve(
        query.history,
        query_features,
        query.intent,
        memory,
        RetrievalConfig(alpha=0.5, gamma=120.0, top_k=3, intent_weight=0.25),
    )

    print("课程03：组合检索")
    print(f"查询意图: {query.intent}")
    for rank, item in enumerate(ranked, start=1):
        print(
            f"Top {rank}: {item.entry.entry_id}, memory_intent={item.entry.intent}, "
            f"cos={item.feature_similarity:.4f}, dtw={item.dtw_distance:.2f}, "
            f"intent_match={item.intent_match:.0f}, score={item.final_score:.4f}"
        )

    # 实践：分别把 alpha 改成 0 和 1，解释排名为什么改变。


if __name__ == "__main__":
    main()

