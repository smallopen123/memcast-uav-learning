from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .features import translation_invariant_path
from .memory import ExperienceMemory, MemoryEntry


@dataclass(frozen=True)
class RetrievalConfig:
    alpha: float = 0.5
    gamma: float = 100.0
    top_k: int = 3
    confidence_weight: float = 1.0
    intent_weight: float = 0.2

    def __post_init__(self) -> None:
        if not 0.0 <= self.alpha <= 1.0:
            raise ValueError("alpha must be in [0, 1]")
        if self.gamma <= 0 or self.top_k <= 0:
            raise ValueError("gamma and top_k must be positive")


@dataclass(frozen=True)
class RetrievalResult:
    entry: MemoryEntry
    feature_similarity: float
    dtw_distance: float
    structural_similarity: float
    intent_match: float
    final_score: float


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float).reshape(-1)
    b = np.asarray(right, dtype=float).reshape(-1)
    if a.shape != b.shape or a.size == 0:
        raise ValueError("feature vectors must have equal non-zero shape")
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return 0.0 if denominator == 0.0 else float(np.dot(a, b) / denominator)


def dtw_distance(left: np.ndarray, right: np.ndarray) -> float:
    """Multivariate DTW using Euclidean point cost."""

    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[1]:
        raise ValueError("DTW inputs must have shape [time, dimensions]")
    previous = np.full(len(b) + 1, np.inf)
    previous[0] = 0.0
    for point_a in a:
        current = np.full(len(b) + 1, np.inf)
        for column, point_b in enumerate(b, start=1):
            cost = float(np.linalg.norm(point_a - point_b))
            current[column] = cost + min(current[column - 1], previous[column], previous[column - 1])
        previous = current
    return float(previous[-1])


def retrieve(
    query_history: np.ndarray,
    query_features: np.ndarray,
    query_intent: str,
    memory: ExperienceMemory,
    config: RetrievalConfig,
) -> list[RetrievalResult]:
    query_path = translation_invariant_path(query_history)
    ranked: list[RetrievalResult] = []
    for entry in memory.entries:
        feature_similarity = cosine_similarity(query_features, entry.features)
        distance = dtw_distance(query_path, entry.relative_history)
        structural = math.exp(-distance / config.gamma)
        base_score = config.alpha * feature_similarity + (1.0 - config.alpha) * structural
        intent_match = 1.0 if entry.intent == query_intent else 0.0
        final_score = (
            base_score
            + config.confidence_weight * entry.confidence
            + config.intent_weight * intent_match
        )
        ranked.append(
            RetrievalResult(
                entry=entry,
                feature_similarity=feature_similarity,
                dtw_distance=distance,
                structural_similarity=structural,
                intent_match=intent_match,
                final_score=final_score,
            )
        )
    ranked.sort(key=lambda item: item.final_score, reverse=True)
    return ranked[: config.top_k]
