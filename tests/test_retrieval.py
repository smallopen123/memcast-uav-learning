from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.features import extract_motion_features
from memcast_uav.memory import build_memory
from memcast_uav.retrieval import RetrievalConfig, retrieve


def test_retrieval_returns_sorted_top_k() -> None:
    sequence = make_synthetic_flight()
    train, test = make_train_test_windows(sequence, split_index=504)
    memory = build_memory(train, limit=30)
    query = test[0]
    ranked = retrieve(
        query.history,
        extract_motion_features(query.history, query.dt),
        query.intent,
        memory,
        RetrievalConfig(top_k=3, gamma=120.0),
    )
    assert len(ranked) == 3
    assert [item.final_score for item in ranked] == sorted(
        [item.final_score for item in ranked],
        reverse=True,
    )


def test_intent_bonus_can_promote_matching_memory() -> None:
    sequence = make_synthetic_flight()
    train, test = make_train_test_windows(sequence, split_index=504)
    memory = build_memory(train, limit=30)
    query = test[0]
    ranked = retrieve(
        query.history,
        extract_motion_features(query.history, query.dt),
        query.intent,
        memory,
        RetrievalConfig(top_k=3, gamma=120.0, intent_weight=2.0),
    )
    assert ranked[0].entry.intent == query.intent

