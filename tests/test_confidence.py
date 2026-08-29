from memcast_uav.confidence import CausalConfidenceQueue, FeedbackEvent
from memcast_uav.data import make_synthetic_flight, make_train_test_windows
from memcast_uav.memory import build_memory


def test_confidence_update_waits_for_available_at() -> None:
    sequence = make_synthetic_flight()
    train, test = make_train_test_windows(sequence, split_index=504)
    memory = build_memory(train, limit=3)
    target = memory.entries[0]
    queue = CausalConfidenceQueue()
    queue.add(
        FeedbackEvent(
            event_id="feedback-0",
            available_at=test[0].forecast_end,
            contributing_ids=[target.entry_id],
            feedback={"success": True},
        )
    )
    assert queue.apply_available(test[0].forecast_start, memory) == 0
    assert target.confidence == 0.0
    assert queue.apply_available(test[0].forecast_end, memory) == 1
    assert target.confidence == 0.01


def test_failed_prediction_does_not_increase_confidence() -> None:
    sequence = make_synthetic_flight()
    train, test = make_train_test_windows(sequence, split_index=504)
    memory = build_memory(train, limit=3)
    target = memory.entries[0]
    queue = CausalConfidenceQueue()
    queue.add(
        FeedbackEvent(
            event_id="feedback-failed",
            available_at=test[0].forecast_end,
            contributing_ids=[target.entry_id],
            feedback={"success": False},
        )
    )
    assert queue.apply_available(test[0].forecast_end, memory) == 0
    assert target.confidence == 0.0

