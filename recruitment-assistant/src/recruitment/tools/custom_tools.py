"""
Recruitment Assistant - Custom Tool Implementations

This module provides real tool wrappers for the recruitment workflow:
- SerperDevTool: Web search for candidate profiles
- ScrapeWebsiteTool: Extract candidate information from web pages
- Error handling with exponential backoff retry logic
- Tool availability checks with graceful degradation

Per PRD §5.2 (NFR-002): Retry with exponential backoff (1s, 2s, 4s, max 3 retries)
"""

import os
import time
import logging
from typing import Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Retry decorator with exponential backoff (PRD §5.2)
# ---------------------------------------------------------------------------

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator that retries a function with exponential backoff.

    Per PRD §5.2: 1s, 2s, 4s, max 3 retries.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)
        max_delay: Maximum delay cap in seconds (default: 10.0)
        exceptions: Tuple of exception types to catch and retry
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(
                            f"[{func.__name__}] Attempt {attempt + 1}/{max_retries + 1} "
                            f"failed: {e}. Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"[{func.__name__}] All {max_retries + 1} attempts failed: {e}"
                        )
            raise last_exception

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Tool availability check
# ---------------------------------------------------------------------------

def check_tool_availability(tool_name: str) -> bool:
    """
    Check if a tool's required dependencies/API keys are available.

    Args:
        tool_name: Name of the tool to check ("serper" or "scrape")

    Returns:
        True if tool is available, False otherwise
    """
    if tool_name == "serper":
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            logger.warning("SERPER_API_KEY not set — SerperDevTool unavailable")
            return False
        try:
            from crewai_tools import SerperDevTool  # noqa: F401
            return True
        except ImportError:
            logger.warning("crewai_tools not installed — SerperDevTool unavailable")
            return False

    elif tool_name == "scrape":
        try:
            from crewai_tools import ScrapeWebsiteTool  # noqa: F401
            return True
        except ImportError:
            logger.warning("crewai_tools not installed — ScrapeWebsiteTool unavailable")
            return False

    return False


# ---------------------------------------------------------------------------
# Tool factory — creates properly configured tool instances
# ---------------------------------------------------------------------------

def get_tools_for_agent(agent_key: str) -> list:
    """
    Create and return the appropriate tool instances for a given agent.

    Per PRD §4.1:
      - researcher:  SerperDevTool, ScrapeWebsiteTool
      - matcher:     SerperDevTool, ScrapeWebsiteTool
      - communicator: SerperDevTool, ScrapeWebsiteTool
      - reporter:    No tools (synthesis only)

    If a tool's API key is missing or the package is not installed,
    the tool is silently skipped (graceful degradation per PRD §5.2).

    Args:
        agent_key: One of "researcher", "matcher", "communicator", "reporter"

    Returns:
        List of configured tool instances
    """
    tools = []

    # Reporter uses no tools — pure synthesis
    if agent_key == "reporter":
        return tools

    # All other agents get search + scrape tools
    if check_tool_availability("serper"):
        try:
            from crewai_tools import SerperDevTool
            serper_tool = SerperDevTool()
            tools.append(serper_tool)
            logger.info(f"[{agent_key}] SerperDevTool initialized")
        except Exception as e:
            logger.warning(f"[{agent_key}] Failed to initialize SerperDevTool: {e}")

    if check_tool_availability("scrape"):
        try:
            from crewai_tools import ScrapeWebsiteTool
            scrape_tool = ScrapeWebsiteTool()
            tools.append(scrape_tool)
            logger.info(f"[{agent_key}] ScrapeWebsiteTool initialized")
        except Exception as e:
            logger.warning(f"[{agent_key}] Failed to initialize ScrapeWebsiteTool: {e}")

    if not tools:
        logger.warning(
            f"[{agent_key}] No tools available. Agent will rely on LLM knowledge only."
        )

    return tools


# ---------------------------------------------------------------------------
# Legacy tool classes (kept for backward compatibility / future use)
# ---------------------------------------------------------------------------

class CandidateSearchTool:
    """
    Tool for searching and extracting candidate information.

    This tool wraps web search functionality to find candidates
    matching specific job requirements. It uses SerperDevTool internally
    with retry logic per PRD §5.2.
    """

    def __init__(self):
        """Initialize the candidate search tool."""
        self.name = "CandidateSearchTool"
        self.description = "Search for candidates matching job requirements"
        self._serper_tool = None

        if check_tool_availability("serper"):
            try:
                from crewai_tools import SerperDevTool
                self._serper_tool = SerperDevTool()
            except ImportError:
                pass

    @retry_with_backoff(max_retries=3, base_delay=1.0, exceptions=(Exception,))
    def search_candidates(self, job_requirements: str) -> dict[str, Any]:
        """
        Search for candidates based on job requirements.

        Args:
            job_requirements: Job requirements string

        Returns:
            Dictionary containing search results

        Raises:
            RuntimeError: If SerperDevTool is unavailable
        """
        if self._serper_tool is None:
            raise RuntimeError(
                "SerperDevTool is not available. Set SERPER_API_KEY environment variable."
            )

        search_query = f"candidates for {job_requirements}"
        result = self._serper_tool.run(search_query)

        return {
            "results": result,
            "search_query": search_query,
            "tool": "serper",
        }


class CandidateScoringTool:
    """
    Tool for scoring and ranking candidates.

    This tool evaluates candidates against job requirements
    and provides scoring with justification.
    """

    def __init__(self):
        """Initialize the candidate scoring tool."""
        self.name = "CandidateScoringTool"
        self.description = "Score and rank candidates against job requirements"

    def score_candidate(self, candidate: dict[str, Any], job_requirements: str) -> dict[str, Any]:
        """
        Score a candidate against job requirements.

        This is a helper used by the Matcher agent's LLM reasoning.
        The actual scoring is performed by the LLM; this provides structure.

        Args:
            candidate: Candidate information dictionary
            job_requirements: Job requirements string

        Returns:
            Dictionary containing score and justification
        """
        return {
            "candidate_id": candidate.get("id", "unknown"),
            "dimensions": {
                "skills_match": 0,
                "experience_level": 0,
                "education": 0,
                "location": 0,
                "additional_factors": 0,
            },
            "overall_score": 0,
            "justification": "Scoring performed by Matcher agent LLM",
        }


class OutreachTemplateTool:
    """
    Tool for generating outreach templates.

    This tool creates personalized outreach messages
    for engaging with candidates.
    """

    def __init__(self):
        """Initialize the outreach template tool."""
        self.name = "OutreachTemplateTool"
        self.description = "Generate personalized outreach templates for candidates"

    def generate_template(self, candidate: dict[str, Any], job_requirements: str) -> dict[str, Any]:
        """
        Generate outreach template for a candidate.

        Args:
            candidate: Candidate information dictionary
            job_requirements: Job requirements string

        Returns:
            Dictionary containing outreach templates
        """
        return {
            "candidate_id": candidate.get("id", "unknown"),
            "initial_contact": "Template generated by Communicator agent LLM",
            "follow_up_sequence": [],
            "interview_invitation": "Template generated by Communicator agent LLM",
            "personalization_tokens": {},
        }


# ---------------------------------------------------------------------------
# Tool registry for easy access
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    "candidate_search": CandidateSearchTool,
    "candidate_scoring": CandidateScoringTool,
    "outreach_template": OutreachTemplateTool,
}


def get_tool(tool_name: str) -> Any:
    """
    Get a tool instance by name.

    Args:
        tool_name: Name of the tool to retrieve

    Returns:
        Tool instance

    Raises:
        ValueError: If tool name is not found
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Tool not found: {tool_name}. Available tools: {list(TOOL_REGISTRY.keys())}")

    return TOOL_REGISTRY[tool_name]()


# ---------------------------------------------------------------------------
# Module self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Custom Tools — Tool Availability Check")
    print("=" * 50)

    print(f"  SerperDevTool available:  {check_tool_availability('serper')}")
    print(f"  ScrapeWebsiteTool available: {check_tool_availability('scrape')}")
    print()

    for agent_key in ["researcher", "matcher", "communicator", "reporter"]:
        tools = get_tools_for_agent(agent_key)
        tool_names = [type(t).__name__ for t in tools]
        print(f"  {agent_key:15s} → {tool_names if tool_names else 'No tools (synthesis only)'}")
