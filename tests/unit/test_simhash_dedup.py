"""Tests for SimHash deduplication with LSH bucketing."""

from src.dedup.simhash_dedup import Deduplicator, NUM_BANDS


def test_identical_texts_are_duplicates():
    dedup = Deduplicator()
    text = "The quick brown fox jumps over the lazy dog near the river bank."
    assert dedup.is_duplicate(text) is False
    assert dedup.is_duplicate(text) is True


def test_normalized_near_duplicates_detected():
    dedup = Deduplicator()
    text1 = "The Quick  Brown   FOX jumps over the lazy dog."
    text2 = "the quick brown fox jumps over the lazy dog."
    assert dedup.is_duplicate(text1) is False
    assert dedup.is_duplicate(text2) is True


def test_different_texts_are_unique():
    dedup = Deduplicator()
    text1 = "Machine learning enables computers to learn from data automatically."
    text2 = "Quantum computing leverages qubits for parallel computation tasks."
    assert dedup.is_duplicate(text1) is False
    assert dedup.is_duplicate(text2) is False


def test_empty_text_is_duplicate():
    dedup = Deduplicator()
    assert dedup.is_duplicate("") is True
    assert dedup.is_duplicate("   ") is True


def test_lsh_buckets_used():
    dedup = Deduplicator()
    for index in range(50):
        text = (
            f"Topic {index}: "
            + " ".join(
                f"term{word_index}z{index}" for word_index in range(15)
            )
        )
        assert dedup.is_duplicate(text) is False
    assert len(dedup._buckets) > NUM_BANDS


def test_eviction_keeps_bucket_indices_consistent():
    dedup = Deduplicator(max_fingerprints=3)
    for index in range(10):
        text = (
            f"Unique document number {index} with distinct vocabulary terms "
            f"alpha beta gamma delta epsilon zeta eta theta."
        )
        dedup.is_duplicate(text)

    assert len(dedup._hashes) == 3
    for indices in dedup._buckets.values():
        assert all(0 <= idx < len(dedup._hashes) for idx in indices)


def test_max_fingerprints_evicts_oldest_fifo():
    dedup = Deduplicator(max_fingerprints=3)
    texts = [
        "Alpha bravo charlie delta echo foxtrot golf hotel.",
        "One two three four five six seven eight nine ten.",
        "Red orange yellow green blue indigo violet spectrum hues.",
        "Machine learning models require diverse training datasets.",
    ]

    for text in texts[:3]:
        assert dedup.is_duplicate(text) is False

    assert len(dedup._hashes) == 3
    assert dedup.is_duplicate(texts[3]) is False
    assert len(dedup._hashes) == 3
    assert dedup.is_duplicate(texts[1]) is True
    assert dedup.is_duplicate(texts[2]) is True
    assert dedup.is_duplicate(texts[0]) is False
