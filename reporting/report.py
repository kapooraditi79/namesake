"""Reads results/<run_id>/results.csv (and, from Phase 3, multiple run_ids
at once) and prints/exports a comparison table.

TODO (Phase 2): print_table(results_csv_path) -> rich table: pass rate,
    avg iterations, avg tokens, avg cost per task.
TODO (Phase 3): compare_table(*results_csv_paths) -> side-by-side columns
    per agent config, plus a regressions column (tasks that flipped
    pass -> fail relative to the first config given, treated as baseline).
"""

from __future__ import annotations


def print_table(results_csv_path: str) -> None:
    raise NotImplementedError


def compare_table(*results_csv_paths: str) -> None:
    raise NotImplementedError
