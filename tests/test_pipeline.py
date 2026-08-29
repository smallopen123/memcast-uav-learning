import math

from memcast_uav.pipeline import run_demo


def test_offline_demo_runs_end_to_end() -> None:
    result = run_demo(test_limit=4)
    assert result.samples == 4
    assert result.memory_entries == 30
    assert math.isfinite(result.mse)
    assert math.isfinite(result.baseline_mse)
    assert result.accepted_candidates + result.rejected_candidates == 4 * result.samples

