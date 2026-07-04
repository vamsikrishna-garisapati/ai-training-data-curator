"""SimHash-based near-duplicate detection with LSH bucketing."""

from __future__ import annotations

from collections import defaultdict

from simhash import Simhash

NUM_BANDS = 4
BAND_WIDTH = 16


class Deduplicator:
    """Track seen content fingerprints and detect near-duplicates via LSH."""

    def __init__(self, threshold: int = 3, max_fingerprints: int = 50_000) -> None:
        self.threshold = threshold
        self.max_fingerprints = max_fingerprints
        self._hashes: list[Simhash] = []
        self._buckets: dict[tuple[int, int], list[int]] = defaultdict(list)

    def _normalize(self, text: str) -> str:
        return " ".join(text.lower().split())

    def _band_keys(self, simhash: Simhash) -> list[tuple[int, int]]:
        value = simhash.value
        mask = (1 << BAND_WIDTH) - 1
        return [
            (band, (value >> (band * BAND_WIDTH)) & mask)
            for band in range(NUM_BANDS)
        ]

    def _remove_index_from_buckets(self, removed_idx: int) -> None:
        """Drop ``removed_idx`` and shift higher indices down by one."""
        empty_keys: list[tuple[int, int]] = []
        for key, indices in self._buckets.items():
            updated = [idx - 1 for idx in indices if idx != removed_idx]
            if updated:
                self._buckets[key] = updated
            else:
                empty_keys.append(key)
        for key in empty_keys:
            del self._buckets[key]

    def _evict_oldest(self) -> None:
        if not self._hashes:
            return
        self._remove_index_from_buckets(0)
        self._hashes.pop(0)

    def is_duplicate(self, text: str) -> bool:
        """Return True if text is a near-duplicate of previously seen content."""
        normalized = self._normalize(text)
        if not normalized:
            return True

        current = Simhash(normalized.split())
        candidate_indices: set[int] = set()
        for key in self._band_keys(current):
            candidate_indices.update(self._buckets[key])

        for idx in candidate_indices:
            if current.distance(self._hashes[idx]) <= self.threshold:
                return True

        while len(self._hashes) >= self.max_fingerprints:
            self._evict_oldest()

        new_idx = len(self._hashes)
        self._hashes.append(current)
        for key in self._band_keys(current):
            self._buckets[key].append(new_idx)
        return False
