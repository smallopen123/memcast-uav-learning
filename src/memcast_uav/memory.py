from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .data import TrajectoryWindow
from .features import extract_motion_features, translation_invariant_path


@dataclass
class MemoryEntry:
    entry_id: str
    history: np.ndarray
    future: np.ndarray
    features: np.ndarray
    intent: str
    strategy: str
    confidence: float = 0.0

    def __post_init__(self) -> None:
        self.history = np.asarray(self.history, dtype=float)
        self.future = np.asarray(self.future, dtype=float)
        self.features = np.asarray(self.features, dtype=float)
        if self.history.ndim != 2 or self.history.shape[1] != 3:
            raise ValueError("memory history must have shape [time, 3]")
        if self.future.ndim != 2 or self.future.shape[1] != 3:
            raise ValueError("memory future must have shape [time, 3]")
        if not np.isfinite(self.confidence):
            raise ValueError("confidence must be finite")

    @property
    def relative_history(self) -> np.ndarray:
        return translation_invariant_path(self.history)

    @property
    def future_displacement(self) -> np.ndarray:
        return self.future - self.history[-1]


@dataclass
class ExperienceMemory:
    entries: list[MemoryEntry] = field(default_factory=list)

    def add(self, entry: MemoryEntry) -> None:
        if any(existing.entry_id == entry.entry_id for existing in self.entries):
            raise ValueError(f"duplicate memory id: {entry.entry_id}")
        self.entries.append(entry)

    def get(self, entry_id: str) -> MemoryEntry:
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        raise KeyError(entry_id)

    def update_confidence(self, entry_ids: list[str], delta: float) -> int:
        wanted = set(entry_ids)
        updated = 0
        for entry in self.entries:
            if entry.entry_id in wanted:
                entry.confidence += float(delta)
                updated += 1
        return updated


def build_memory(windows: list[TrajectoryWindow], limit: int = 30) -> ExperienceMemory:
    """Turn the most recent training windows into experience entries."""

    selected = windows[-limit:]
    memory = ExperienceMemory()
    for window in selected:
        memory.add(
            MemoryEntry(
                entry_id=f"memory-{window.sample_id}",
                history=window.history,
                future=window.future,
                features=extract_motion_features(window.history, window.dt),
                intent=window.intent,
                strategy=f"reuse observed {window.intent} displacement pattern",
            )
        )
    return memory

