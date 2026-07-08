#!/usr/bin/env python3
"""
upgrade.py — QA-04 Fix: Refactor RecruitmentCrew to Lazy-Init Singleton.

Addresses the double-initialization issue in main.py lines 354 and 379
by providing a lazy singleton pattern for RecruitmentCrew.

The issue:
  main.py:354 — RecruitCrew() created inside Status context
  main.py:379 — Crew.kickoff() called on the same instance

This script provides a drop-in replacement that ensures RecruitmentCrew
is initialized only once. It does NOT modify existing files — it serves
as a reference implementation for the backend engineer to integrate.

Usage:
    uv run python scripts/upgrade.py --help
    uv run python scripts/upgrade.py --preview  # Show the refactored pattern

Strangler Fig: This script does NOT modify any existing Python files.
"""

import argparse
import textwrap


SINGLETON_PATCH = textwrap.dedent("""\
# ── Singleton patch (QA-04) ──────────────────────────────────
# Replace the double-init in run_workflow() with lazy initialization.
# 
# Before (main.py:338-389):
#     def run_workflow(job_desc):
#         from recruitment.crew import RecruitmentCrew
#         ...
#         with Status(...):                         # line 354
#             crew = RecruitmentCrew()              # FIRST init
#             time.sleep(0.5)
#         ...
#         for emoji, name, task in agents:          # lines 373-376
#             with Status(...):
#                 time.sleep(1)                     # simulated spinner
#         report = crew.kickoff(job_requirements)   # line 379 — SECOND use
#
# After:
#     _crew_instance = None
#
#     def get_crew():
#         global _crew_instance
#         if _crew_instance is None:
#             _crew_instance = RecruitmentCrew()
#         return _crew_instance
#
#     def run_workflow(job_desc):
#         from recruitment.crew import RecruitmentCrew
#         ...
#         crew = get_crew()  # lazy init, single instance
#         ...
#         report = crew.kickoff(job_requirements)
""")


def preview_patch():
    """Print the singleton patch pattern for manual integration."""
    print("=" * 70)
    print("QA-04 Fix: RecruitmentCrew Lazy-Init Singleton")
    print("=" * 70)
    print()
    print("This patch addresses the double RecruitmentCrew initialization")
    print("identified in main.py:354 (first init) and main.py:379 (second use).")
    print()
    print(SINGLETON_PATCH)
    print()
    print("Integration steps:")
    print("  1. Open recruitment-assistant/src/recruitment/main.py")
    print("  2. Add the singleton pattern near the top of the file")
    print("  3. Replace `crew = RecruitmentCrew()` with `crew = get_crew()`")
    print("  4. Remove the simulated spinner loop (lines 373-376)")
    print("  5. Verify: uv run recruitment still works")
    print()
    print("See qa-plan.md §7.2 for full details on QA-04.")


def main():
    parser = argparse.ArgumentParser(
        description="QA-04 Fix: RecruitmentCrew Lazy-Init Singleton Refactor",
        epilog="This script is a reference; it does NOT modify any existing files.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the singleton patch pattern (default action)",
    )
    args = parser.parse_args()

    if args.preview:
        preview_patch()
    else:
        preview_patch()


if __name__ == "__main__":
    main()
