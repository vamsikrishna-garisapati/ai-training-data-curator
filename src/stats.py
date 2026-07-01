"""Run-level crawl statistics for summary export."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CrawlStats:
    """Track pages crawled, saved, filtered, and failed."""

    crawled: int = 0
    saved: int = 0
    filtered_extraction: int = 0
    filtered_language: int = 0
    filtered_length: int = 0
    filtered_quality: int = 0
    filtered_dedup: int = 0
    failed: int = 0

    def to_summary(self, max_pages: int, final_stats=None) -> dict:
        """Serialize stats for key-value store export."""
        summary = {
            "crawled": self.crawled,
            "saved": self.saved,
            "filtered": {
                "extraction": self.filtered_extraction,
                "language": self.filtered_language,
                "length": self.filtered_length,
                "quality": self.filtered_quality,
                "dedup": self.filtered_dedup,
            },
            "failed": self.failed,
            "maxPages": max_pages,
        }
        if final_stats is not None:
            summary["requestsFinished"] = final_stats.requests_finished
            summary["requestsFailed"] = final_stats.requests_failed
            summary["requestsTotal"] = final_stats.requests_total
        return summary
