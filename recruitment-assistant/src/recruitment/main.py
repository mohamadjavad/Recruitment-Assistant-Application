"""
Recruitment Assistant - Main Entry Point

This module provides the CLI interface for the recruitment assistant.
It handles user input, validates job descriptions, and orchestrates
the multi-agent workflow.

Usage:
    uv run recruitment
    python -m recruitment.main
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.spinner import Spinner
from rich.status import Status
from rich.markdown import Markdown
from rich.text import Text
from rich import box

# Load environment variables
load_dotenv()

console = Console()


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def validate_job_description(job_desc: dict) -> list[str]:
    """
    Validate that the job description contains all required fields.
    
    Per PRD §4.2:
    - Job title (required)
    - Job description (minimum 100 characters)
    - Key responsibilities (minimum 3 items)
    - Required qualifications (minimum 3 items)
    - Preferred qualifications (optional)
    - Perks and benefits (optional)
    
    Args:
        job_desc: Dictionary containing job description fields
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate required fields exist and are non-empty
    required_fields = {
        "title": "Job title",
        "description": "Job description",
        "responsibilities": "Key responsibilities",
        "qualifications": "Required qualifications"
    }
    
    for field, display_name in required_fields.items():
        if field not in job_desc or not job_desc[field]:
            errors.append(f"Missing required field: {display_name}")
    
    # Validate minimum lengths if fields exist
    if job_desc.get("description") and len(job_desc["description"]) < 100:
        errors.append(f"Job description must be at least 100 characters (currently {len(job_desc['description'])} characters)")
    
    if job_desc.get("responsibilities") and len(job_desc["responsibilities"]) < 3:
        errors.append(f"At least 3 responsibilities required (currently {len(job_desc['responsibilities'])})")
    
    if job_desc.get("qualifications") and len(job_desc["qualifications"]) < 3:
        errors.append(f"At least 3 qualifications required (currently {len(job_desc['qualifications'])})")
    
    return errors


def collect_job_title() -> str:
    """Collect job title from user."""
    while True:
        title = Prompt.ask("\n[bold green]Job Title[/bold green]")
        if title.strip():
            return title.strip()
        console.print("[red]Job title cannot be empty. Please enter a job title.[/red]")


def collect_job_description() -> str:
    """Collect multi-line job description from user."""
    console.print("\n[bold green]Job Description[/bold green]")
    console.print("[dim]Minimum 100 characters. Press Enter twice when finished.[/dim]")
    
    lines = []
    empty_count = 0
    
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append(line)
        else:
            empty_count = 0
            lines.append(line)
    
    description = "\n".join(lines).strip()
    
    # Show character count
    char_count = len(description)
    if char_count >= 100:
        console.print(f"[green]✓ Description recorded ({char_count} characters)[/green]")
    else:
        console.print(f"[yellow]⚠ Description is {char_count} characters (minimum 100 required)[/yellow]")
    
    return description


def collect_list_input(field_name: str, min_items: int = 3) -> list[str]:
    """
    Collect a list of items from user.
    
    Args:
        field_name: Display name for the field
        min_items: Minimum number of items required
        
    Returns:
        List of items entered by user
    """
    console.print(f"\n[bold green]{field_name}[/bold green]")
    console.print(f"[dim]Enter each item, then press Enter on empty line to finish (minimum {min_items} items).[/dim]")
    
    items = []
    while True:
        item = Prompt.ask(f"[green]{field_name[:-1] if field_name.endswith('s') else field_name}[/green]", default="")
        if item == "":
            if len(items) >= min_items:
                break
            else:
                console.print(f"[yellow]Please enter at least {min_items} items (currently {len(items)} entered)[/yellow]")
        else:
            items.append(item.strip())
            console.print(f"[dim]  Added: {item.strip()}[/dim]")
    
    console.print(f"[green]✓ {len(items)} items recorded[/green]")
    return items


def collect_optional_list(field_name: str) -> list[str]:
    """
    Collect an optional list of items from user.
    
    Args:
        field_name: Display name for the field
        
    Returns:
        List of items entered by user (empty if skipped)
    """
    if not Confirm.ask(f"\n[green]Would you like to add {field_name.lower()}?[/green]", default=False):
        return []
    
    console.print(f"[dim]Enter each item, then press Enter on empty line to finish.[/dim]")
    
    items = []
    while True:
        item = Prompt.ask(f"[green]{field_name[:-1] if field_name.endswith('s') else field_name}[/green]", default="")
        if item == "":
            break
        items.append(item.strip())
        console.print(f"[dim]  Added: {item.strip()}[/dim]")
    
    if items:
        console.print(f"[green]✓ {len(items)} items recorded[/green]")
    return items


def collect_job_description_interactive() -> dict:
    """
    Collect complete job description from user via interactive prompts.
    
    Returns:
        Dictionary containing job description fields
    """
    console.print(Panel.fit(
        "[bold blue]📋 Job Description Input[/bold blue]\n"
        "[dim]Please provide the following details about the position.[/dim]",
        border_style="blue"
    ))
    
    job_desc = {}
    
    # Collect required fields
    job_desc["title"] = collect_job_title()
    job_desc["description"] = collect_job_description()
    job_desc["responsibilities"] = collect_list_input("Key Responsibilities", min_items=3)
    job_desc["qualifications"] = collect_list_input("Required Qualifications", min_items=3)
    
    # Collect optional fields
    job_desc["preferred_qualifications"] = collect_optional_list("Preferred Qualifications")
    job_desc["perks"] = collect_optional_list("Perks and Benefits")
    
    return job_desc


def format_job_requirements(job_desc: dict) -> str:
    """
    Format job description into a readable string for the crew.
    
    Args:
        job_desc: Dictionary containing job description fields
        
    Returns:
        Formatted string
    """
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


def display_input_summary(job_desc: dict) -> None:
    """
    Display a formatted summary of the collected job description.
    
    Args:
        job_desc: Dictionary containing job description fields
    """
    console.print("\n[bold]📝 Job Description Summary[/bold]")
    
    table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
    table.add_column("Field", style="green", width=25)
    table.add_column("Value")
    
    table.add_row("Title", job_desc["title"])
    table.add_row("Description", job_desc["description"][:100] + "..." if len(job_desc["description"]) > 100 else job_desc["description"])
    table.add_row("Responsibilities", f"{len(job_desc['responsibilities'])} items")
    table.add_row("Qualifications", f"{len(job_desc['qualifications'])} items")
    
    if job_desc.get("preferred_qualifications"):
        table.add_row("Preferred Qualifications", f"{len(job_desc['preferred_qualifications'])} items")
    if job_desc.get("perks"):
        table.add_row("Perks and Benefits", f"{len(job_desc['perks'])} items")
    
    console.print(table)


def display_report(report_path: str, report_content: str) -> None:
    """
    Display the generated candidate report.
    
    Args:
        report_path: Path to the report file
        report_content: Content of the report
    """
    console.print(Panel.fit(
        "[bold green]✅ Candidate Report Generated Successfully![/bold green]",
        border_style="green"
    ))
    
    console.print(Panel(
        Markdown(report_content),
        title="[bold]📄 Candidate Report[/bold]",
        border_style="blue",
        padding=(1, 2)
    ))
    
    console.print(f"\n[dim]📁 Report saved to: {report_path}[/dim]")


def display_error(message: str, suggestion: Optional[str] = None) -> None:
    """
    Display an error message with optional suggestion.
    
    Args:
        message: Error message
        suggestion: Optional suggestion for fixing the error
    """
    error_text = f"[bold red]❌ Error:[/bold red] {message}"
    if suggestion:
        error_text += f"\n\n[yellow]💡 Suggestion:[/yellow] {suggestion}"
    
    console.print(Panel(error_text, border_style="red"))


def display_workflow_start() -> None:
    """Display workflow start message."""
    console.print("\n" + "=" * 60)
    console.print("[bold blue]🚀 Starting Recruitment Workflow[/bold blue]")
    console.print("[dim]This may take a few minutes. Please wait...[/dim]")
    console.print("=" * 60)


def display_workflow_complete(report_path: str, duration: float) -> None:
    """
    Display workflow completion message.
    
    Args:
        report_path: Path to the generated report
        duration: Time taken in seconds
    """
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    
    console.print("\n" + "=" * 60)
    console.print("[bold green]✅ Workflow Complete![/bold green]")
    console.print(f"[dim]⏱  Time taken: {minutes}m {seconds}s[/dim]")
    console.print(f"[dim]📁 Report: {report_path}[/dim]")
    console.print("=" * 60)


def run_workflow(job_desc: dict) -> str:
    """
    Execute the recruitment workflow.
    
    Args:
        job_desc: Dictionary containing job description fields
        
    Returns:
        Final report as string
    """
    from recruitment.crew import RecruitmentCrew
    
    # Format job requirements
    job_requirements = format_job_requirements(job_desc)
    
    # Initialize crew
    with Status("[bold blue]Initializing recruitment crew...", console=console, spinner="dots"):
        crew = RecruitmentCrew()
        time.sleep(0.5)  # Brief pause for visual feedback
    
    # Execute workflow with progress display
    start_time = time.time()
    
    console.print("\n[bold]🤖 Agent Workflow Progress[/bold]")
    console.print("[dim]Sequential execution: Researcher → Matcher → Communicator → Reporter[/dim]\n")
    
    try:
        # Display agent progress
        agents = [
            ("🔍", "Researcher", "Searching for candidates..."),
            ("📊", "Matcher", "Scoring and ranking candidates..."),
            ("💬", "Communicator", "Generating outreach strategy..."),
            ("📝", "Reporter", "Compiling final report...")
        ]
        
        for emoji, name, task in agents:
            with Status(f"{emoji} {name}: {task}", console=console, spinner="dots"):
                # Simulate agent work time (will be replaced with real execution)
                time.sleep(1)
        
        # Execute actual workflow
        report = crew.kickoff(job_requirements)
        
        return report
        
    except Exception as e:
        duration = time.time() - start_time
        display_error(
            f"Workflow execution failed after {duration:.1f}s",
            f"Technical details: {str(e)}\n\nPlease check your API keys and try again."
        )
        raise


def main():
    """
    Main entry point for the recruitment assistant.
    
    Usage:
        uv run recruitment
        python -m recruitment.main
    """
    # Display welcome banner
    console.print(Panel.fit(
        "[bold blue]🤖 Recruitment Assistant[/bold blue]\n"
        "[dim]A CrewAI Multi-Agent System for Recruitment[/dim]\n"
        "[dim]Version 0.1.0[/dim]",
        border_style="blue"
    ))
    
    # Check for required environment variables
    required_env_vars = ["OPENAI_API_KEY", "SERPER_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        display_error(
            f"Missing required environment variables: {', '.join(missing_vars)}",
            "Copy .env.example to .env and fill in your API keys:\n"
            "  copy .env.example .env\n"
            "  # Edit .env with your API keys"
        )
        sys.exit(1)
    
    try:
        # Collect job description
        job_desc = collect_job_description_interactive()
        
        # Validate input
        errors = validate_job_description(job_desc)
        if errors:
            console.print("\n[bold red]❌ Validation Errors:[/bold red]")
            for error in errors:
                console.print(f"  [red]• {error}[/red]")
            console.print("\n[yellow]Please fix the errors and try again.[/yellow]")
            sys.exit(1)
        
        # Display summary and confirm
        display_input_summary(job_desc)
        
        if not Confirm.ask("\n[green]Proceed with recruitment workflow?[/green]", default=True):
            console.print("[yellow]Workflow cancelled by user.[/yellow]")
            sys.exit(0)
        
        # Execute workflow
        display_workflow_start()
        start_time = time.time()
        
        report = run_workflow(job_desc)
        
        duration = time.time() - start_time
        
        # Save report
        report_path = Path("candidate_report.md").absolute()
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        # Display results
        display_workflow_complete(str(report_path), duration)
        display_report(str(report_path), report)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Workflow cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        display_error(
            "An unexpected error occurred",
            f"Technical details: {str(e)}\n\nPlease check the error and try again."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
