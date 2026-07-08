#!/usr/bin/env python3
"""
SSE-aware CLI wrapper for the Recruitment Assistant.

Emits structured JSON events to stdout that the Next.js API route
consumes as an SSE stream. Supports --sse flag for web UI mode
and --input for job description JSON file.

Usage:
    uv run python scripts/run_recruitment_sse.py --sse --input job.json
    uv run python scripts/run_recruitment_sse.py --help

SSE Protocol (stdout lines):
    {"event": "agent_start",      "agent": "Researcher", "task": "TASK-01", ...}
    {"event": "agent_progress",   "agent": "Researcher", "progress": 45, ...}
    {"event": "agent_complete",   "agent": "Researcher", "output": "...", ...}
    {"event": "error",            "code": "...", "message": "...", ...}
    {"event": "report_ready",     "report_path": "...", "size_bytes": 61239, ...}
    {"event": "workflow_complete","status": "success", ...}

Strangler Fig: Does NOT modify existing recruitment/main.py or crew.py.
"""

import argparse
import json
import os
import sys
import time
import tempfile
import warnings
from datetime import datetime, timezone
from pathlib import Path

# Suppress deprecation warnings from CrewAI internals (QA-03 mitigation)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="crewai")

# Ensure the project src directory is on the path
_project_root = Path(__file__).resolve().parent.parent
_src_dir = _project_root / "recruitment-assistant" / "src"
if _src_dir.exists():
    sys.path.insert(0, str(_src_dir))


def emit(event_type: str, **kwargs) -> None:
    """Emit a structured JSON event to stdout."""
    payload = {"event": event_type, "timestamp": datetime.now(timezone.utc).isoformat(), **kwargs}
    sys.stdout.write(json.dumps(payload, default=str) + "\n")
    sys.stdout.flush()


def validate_environment() -> list[str]:
    """Check required env vars and return list of missing keys."""
    required = ["OPENAI_API_KEY", "SERPER_API_KEY"]
    return [var for var in required if not os.getenv(var)]


def load_job_input(filepath: str) -> dict:
    """Load job description from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def validate_job_description(job_desc: dict) -> list[str]:
    """Validate job description fields (mirrors main.py validation)."""
    errors = []
    required_fields = {
        "title": "Job title",
        "description": "Job description",
        "responsibilities": "Key responsibilities",
        "qualifications": "Required qualifications",
    }
    for field, display_name in required_fields.items():
        if field not in job_desc or not job_desc[field]:
            errors.append(f"Missing required field: {display_name}")
    if job_desc.get("description") and len(job_desc["description"]) < 100:
        errors.append(f"Job description must be at least 100 characters")
    if job_desc.get("responsibilities") and len(job_desc["responsibilities"]) < 3:
        errors.append(f"At least 3 responsibilities required")
    if job_desc.get("qualifications") and len(job_desc["qualifications"]) < 3:
        errors.append(f"At least 3 qualifications required")
    return errors


def format_job_requirements(job_desc: dict) -> str:
    """Format job description into a readable string for the crew."""
    parts = [
        f"Job Title: {job_desc['title']}",
        f"\nJob Description:\n{job_desc['description']}",
        f"\nKey Responsibilities:",
    ]
    for i, resp in enumerate(job_desc.get("responsibilities", []), 1):
        parts.append(f"  {i}. {resp}")
    parts.append(f"\nRequired Qualifications:")
    for i, qual in enumerate(job_desc.get("qualifications", []), 1):
        parts.append(f"  {i}. {qual}")
    if job_desc.get("preferred_qualifications"):
        parts.append(f"\nPreferred Qualifications:")
        for i, pref in enumerate(job_desc["preferred_qualifications"], 1):
            parts.append(f"  {i}. {pref}")
    if job_desc.get("perks"):
        parts.append(f"\nPerks and Benefits:")
        for i, perk in enumerate(job_desc["perks"], 1):
            parts.append(f"  {i}. {perk}")
    return "\n".join(parts)


def run_workflow_sse(job_desc: dict) -> str:
    """
    Execute the recruitment workflow with SSE event emission.
    
    Emits events for each agent lifecycle phase and returns the final report.
    """
    from recruitment.crew import RecruitmentCrew

    job_requirements = format_job_requirements(job_desc)

    emit("workflow_start", job_title=job_desc.get("title", "Unknown"))

    # Initialize crew (lazy init — single initialization per QA-04)
    emit("system", message="Initializing recruitment crew...")
    crew = RecruitmentCrew()

    # Simulated agent steps with real SSE events
    # (Will be replaced with actual agent callbacks in v0.4.0+)
    agents_info = [
        ("Researcher", "TASK-01", "Searching for candidates..."),
        ("Matcher", "TASK-02", "Scoring and ranking candidates..."),
        ("Communicator", "TASK-03", "Generating outreach strategy..."),
        ("Reporter", "TASK-04", "Compiling final report..."),
    ]

    start_time = time.time()

    try:
        for agent_name, task_id, task_desc in agents_info:
            emit("agent_start", agent=agent_name, task=task_id, description=task_desc)
            # Simulate incremental progress (3 ticks for demo)
            for pct in [25, 50, 75]:
                time.sleep(0.3)  # brief simulation; real execution will replace this
                emit("agent_progress", agent=agent_name, progress=pct, message=task_desc)
            emit("agent_complete", agent=agent_name, output=f"{agent_name} completed successfully", duration_seconds=1.5)

        # Execute actual crew kickoff
        emit("system", message="Running CrewAI workflow...")
        report = crew.kickoff(job_requirements)

        duration = time.time() - start_time

        # Save report
        report_path = Path("candidate_report.md").absolute()
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        emit("report_ready", report_path=str(report_path), size_bytes=len(report.encode("utf-8")), duration_total=duration)
        emit("workflow_complete", status="success")

        return report

    except Exception as e:
        duration = time.time() - start_time
        emit("error", code="WORKFLOW_ERROR", message=str(e), severity="error")
        emit("workflow_complete", status="error", error=str(e), duration_total=duration)
        raise


def run_cli_interactive(job_desc: dict) -> str:
    """Run the workflow in CLI mode (no SSE)."""
    from recruitment.crew import RecruitmentCrew

    job_requirements = format_job_requirements(job_desc)
    crew = RecruitmentCrew()
    return crew.kickoff(job_requirements)


def main():
    parser = argparse.ArgumentParser(
        description="Recruitment Assistant — SSE-aware CLI Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Web UI mode (SSE events to stdout):
  uv run python scripts/run_recruitment_sse.py --sse --input job.json

  # CLI mode (same as uv run recruitment):
  uv run python scripts/run_recruitment_sse.py --input job.json

  # Check env configuration:
  uv run python scripts/run_recruitment_sse.py --check-env
        """,
    )
    parser.add_argument("--sse", action="store_true", help="Emit SSE-structured JSON events to stdout")
    parser.add_argument("--input", type=str, help="Path to job description JSON file")
    parser.add_argument("--check-env", action="store_true", help="Check environment configuration and exit")
    args = parser.parse_args()

    # Check env mode
    if args.check_env:
        missing = validate_environment()
        if missing:
            print(json.dumps({"configured": False, "missing_keys": missing}))
            sys.exit(1)
        else:
            print(json.dumps({"configured": True, "missing_keys": []}))
            sys.exit(0)

    # Validate environment
    missing = validate_environment()
    if missing:
        if args.sse:
            emit("error", code="MISSING_ENV_VARS", message=f"Missing: {', '.join(missing)}", severity="fatal")
        else:
            print(f"Error: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    # Load job input
    if not args.input:
        print("Error: --input is required (path to job description JSON file)", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    job_desc = load_job_input(args.input)

    # Validate
    errors = validate_job_description(job_desc)
    if errors:
        if args.sse:
            emit("error", code="VALIDATION_ERROR", message="; ".join(errors), severity="fatal")
        else:
            print(f"Validation errors: {'; '.join(errors)}", file=sys.stderr)
        sys.exit(1)

    # Run workflow
    if args.sse:
        run_workflow_sse(job_desc)
    else:
        report = run_cli_interactive(job_desc)
        report_path = Path("candidate_report.md").absolute()
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to {report_path}")
        print(report)


if __name__ == "__main__":
    main()
