"""
src/utils/profiler.py
======================
Lightweight performance profiler for GeneCraft simulation systems.
Tracks per-system tick time and produces a summary report.
"""
from __future__ import annotations
import time
import logging
from collections import defaultdict
from contextlib import contextmanager
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Profiler:
    """
    Simple wall-clock profiler using context managers.

    Usage
    -----
    profiler = Profiler(enabled=True)

    with profiler.section("ai_update"):
        ... AI logic ...

    with profiler.section("genetics"):
        ... genetics logic ...

    profiler.report()   # logs summary
    """

    def __init__(self, enabled: bool = False) -> None:
        self.enabled   = enabled
        self._times:   Dict[str, List[float]] = defaultdict(list)
        self._current: Dict[str, float]       = {}

    @contextmanager
    def section(self, name: str):
        """Context manager that times a named code section."""
        if not self.enabled:
            yield
            return
        t0 = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            self._times[name].append(elapsed_ms)

    def mean(self, name: str) -> float:
        """Return average time in ms for a section over recorded samples."""
        samples = self._times.get(name, [])
        return sum(samples) / len(samples) if samples else 0.0

    def total(self, name: str) -> float:
        return sum(self._times.get(name, []))

    def reset(self) -> None:
        self._times.clear()

    def report(self, top_n: int = 10) -> str:
        """Log and return a formatted performance report."""
        if not self._times:
            return "No profiling data."
        lines = ["─" * 52,
                 f"{'Section':<28} {'Avg ms':>8} {'Total ms':>10}",
                 "─" * 52]
        sorted_sections = sorted(
            self._times.keys(),
            key=lambda k: self.mean(k),
            reverse=True,
        )
        for name in sorted_sections[:top_n]:
            lines.append(
                f"{name:<28} {self.mean(name):>8.2f} {self.total(name):>10.2f}"
            )
        lines.append("─" * 52)
        report = "\n".join(lines)
        logger.info("Profiler Report:\n%s", report)
        return report

    def worst_tick(self, name: str) -> float:
        samples = self._times.get(name, [])
        return max(samples) if samples else 0.0

    def sample_count(self, name: str) -> int:
        return len(self._times.get(name, []))


# Global singleton (disabled by default, enabled via --profile flag)
_global_profiler = Profiler(enabled=False)


def get_profiler() -> Profiler:
    return _global_profiler


def enable_profiling() -> None:
    _global_profiler.enabled = True
    logger.info("Profiler: enabled.")
