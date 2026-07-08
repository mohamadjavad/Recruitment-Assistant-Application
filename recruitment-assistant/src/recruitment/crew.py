"""
Recruitment Assistant - Crew Assembly and Orchestration

This module handles the assembly and orchestration of the CrewAI crew.
It loads agent and task configurations from YAML files and executes
the sequential recruitment workflow.

Workflow (PRD §4.1):
  TASK-01 (Researcher)  →  TASK-02 (Matcher)  →  TASK-03 (Communicator)  →  TASK-04 (Reporter)

Usage:
    from recruitment.crew import RecruitmentCrew

    crew = RecruitmentCrew()
    report = crew.kickoff(job_requirements)
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

logger = logging.getLogger(__name__)


class RecruitmentCrew:
    """
    CrewAI crew for the recruitment workflow.

    This class:
      - Loads agent definitions from config/agents.yaml
      - Loads task definitions from config/tasks.yaml
      - Wires real tools (SerperDevTool, ScrapeWebsiteTool) per agent
      - Assembles a CrewAI Crew with Sequential process
      - Exposes kickoff() for main.py to call

    Attributes:
        config_dir: Path to the configuration directory
        agents_config: Parsed agents YAML
        tasks_config: Parsed tasks YAML
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the recruitment crew.

        Args:
            config_dir: Path to configuration directory (default: config/)

        Raises:
            FileNotFoundError: If configuration files are missing
        """
        if config_dir is None:
            config_dir = Path(__file__).parent / "config"

        self.config_dir = config_dir
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")

        # Populated during kickoff
        self._agents = []
        self._tasks = []
        self._crew = None

    # ------------------------------------------------------------------
    # Configuration loading
    # ------------------------------------------------------------------

    def _load_config(self, filename: str) -> dict:
        """
        Load a YAML configuration file.

        Args:
            filename: Name of the YAML file (relative to config_dir)

        Returns:
            Parsed dictionary

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file is empty or malformed
        """
        config_path = self.config_dir / filename

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Ensure the config directory exists at: {self.config_dir}"
            )

        with open(config_path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)

        if not config:
            raise ValueError(f"Configuration file is empty: {config_path}")

        logger.info(f"Loaded configuration: {filename} ({len(config)} entries)")
        return config

    # ------------------------------------------------------------------
    # Agent creation
    # ------------------------------------------------------------------

    def _create_agents(self) -> list:
        """
        Create CrewAI Agent objects from agents.yaml.

        Tool assignment per PRD §4.1:
          - researcher:   SerperDevTool, ScrapeWebsiteTool
          - matcher:      SerperDevTool, ScrapeWebsiteTool
          - communicator: SerperDevTool, ScrapeWebsiteTool
          - reporter:     No tools (synthesis only)

        Each agent uses the configured LLM (LLM_MODEL + LLM_BASE_URL / OPENAI_BASE_URL)
        so that custom endpoints (e.g. GLM-5.2) are respected.

        Returns:
            List of crewai.Agent instances
        """
        from crewai import Agent, LLM
        from recruitment.tools.custom_tools import get_tools_for_agent

        # Build LLM from environment: LLM_MODEL, LLM_BASE_URL, OPENAI_API_KEY
        llm_model = os.getenv("LLM_MODEL", "gpt-4")
        llm_base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")
        if llm_base_url and not llm_base_url.rstrip("/").endswith("/v1"):
            llm_base_url = llm_base_url.rstrip("/") + "/v1"
        llm_kwargs = {"model": llm_model}
        if llm_base_url:
            llm_kwargs["base_url"] = llm_base_url

        logger.info(
            f"Creating agents with LLM: model={llm_model}, "
            f"base_url={llm_base_url or '(default)'}"
        )
        llm = LLM(**llm_kwargs)

        agents = []

        for agent_key, agent_config in self.agents_config.items():
            tools = get_tools_for_agent(agent_key)

            agent = Agent(
                role=agent_config["role"].strip(),
                goal=agent_config["goal"].strip(),
                backstory=agent_config["backstory"].strip(),
                tools=tools,
                llm=llm,
                verbose=True,
                allow_delegation=False,
            )

            logger.info(
                f"Created agent '{agent_key}': role={agent.role!r}, "
                f"tools={[type(t).__name__ for t in tools]}"
            )
            agents.append(agent)

        return agents

    # ------------------------------------------------------------------
    # Task creation
    # ------------------------------------------------------------------

    def _create_tasks(self, agents: list, job_requirements: str) -> list:
        """
        Create CrewAI Task objects from tasks.yaml with context passing.

        Context chain per PRD §4.1:
          TASK-02 receives TASK-01 output as context
          TASK-03 receives TASK-02 output as context
          TASK-04 receives all previous outputs as context

        Args:
            agents: List of CrewAI Agent objects (same order as agents.yaml)
            job_requirements: Formatted job requirements string

        Returns:
            List of crewai.Task instances
        """
        from crewai import Task

        # Build a mapping from YAML key → agent object
        agent_keys = list(self.agents_config.keys())
        agent_map = {key: agents[i] for i, key in enumerate(agent_keys)}

        # Fixed mapping: task YAML key → agent YAML key
        task_agent_map = {
            "research_candidates_task": "researcher",
            "match_and_score_candidates_task": "matcher",
            "outreach_strategy_task": "communicator",
            "report_candidates_task": "reporter",
        }

        tasks = []
        previous_tasks = []  # accumulate for context passing

        for task_key, task_config in self.tasks_config.items():
            # Resolve agent
            agent_key = task_agent_map.get(task_key)
            if agent_key is None:
                raise ValueError(
                    f"Task '{task_key}' has no agent mapping. "
                    f"Expected one of: {list(task_agent_map.keys())}"
                )
            if agent_key not in agent_map:
                raise ValueError(
                    f"Agent '{agent_key}' (for task '{task_key}') not found in agents.yaml. "
                    f"Available agents: {list(agent_map.keys())}"
                )

            agent = agent_map[agent_key]

            # Format description with job_requirements variable
            description = task_config["description"]
            try:
                description = description.format(job_requirements=job_requirements)
            except KeyError:
                # If {job_requirements} placeholder is missing, append it
                description = f"{description}\n\nJob Requirements:\n{job_requirements}"

            # Context: pass outputs of all prior tasks
            context = previous_tasks if previous_tasks else None

            task = Task(
                description=description,
                expected_output=task_config["expected_output"].strip(),
                agent=agent,
                context=context,
            )

            previous_tasks.append(task)
            tasks.append(task)

            logger.info(
                f"Created task '{task_key}': agent={agent_key}, "
                f"context={'Yes' if context else 'None'}"
            )

        return tasks

    # ------------------------------------------------------------------
    # Crew assembly
    # ------------------------------------------------------------------

    def _create_crew(self, agents: list, tasks: list) -> Any:
        """
        Assemble the CrewAI Crew.

        Configuration per SAD §2.5:
          - Process: Sequential (PRD §10, Assumption 7)
          - Verbose: True (PRD §5.3 — Observable by Default)
          - Memory: In-memory (no persistent storage for MVP)
          - Cache: Enabled (reduces LLM API costs)
          - Max RPM: 10

        Args:
            agents: List of Agent objects
            tasks: List of Task objects

        Returns:
            crewai.Crew instance
        """
        from crewai import Crew, Process

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            max_rpm=10,
        )

        logger.info(
            f"Crew assembled: {len(agents)} agents, {len(tasks)} tasks, "
            f"process=sequential"
        )
        return crew

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def kickoff(self, job_requirements: str) -> str:
        """
        Execute the full recruitment workflow.

        Steps:
          1. Create agents from YAML config + real tools
          2. Create tasks from YAML config with variable interpolation
          3. Assemble Crew with Sequential process
          4. Execute crew.kickoff()
          5. Return the final report

        Args:
            job_requirements: Formatted job requirements string
                              (produced by main.py's format_job_requirements)

        Returns:
            Final candidate report as a markdown string

        Raises:
            ValueError: If job_requirements is empty
            RuntimeError: If workflow execution fails
        """
        if not job_requirements or not job_requirements.strip():
            raise ValueError("Job requirements cannot be empty")

        # Ensure OPENAI_BASE_URL is set for CrewAI internal components
        # that check this env var (memory, LLM calls, etc.)
        llm_base_url = os.getenv("LLM_BASE_URL")
        if llm_base_url and not os.getenv("OPENAI_BASE_URL"):
            os.environ["OPENAI_BASE_URL"] = llm_base_url
            logger.info(f"Set OPENAI_BASE_URL from LLM_BASE_URL: {llm_base_url}")

        logger.info("Starting recruitment workflow...")

        # 1. Create agents
        self._agents = self._create_agents()

        # 2. Create tasks (with context passing)
        self._tasks = self._create_tasks(self._agents, job_requirements)

        # 3. Assemble crew
        self._crew = self._create_crew(self._agents, self._tasks)

        # 4. Execute
        logger.info("Kicking off crew execution...")
        result = self._crew.kickoff()

        logger.info("Workflow completed successfully.")

        # Crew.kickoff() may return an AgentOutput or str; normalise to str
        if hasattr(result, "raw"):
            return result.raw
        return str(result)

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_agent_info(self) -> dict:
        """Return a summary of each configured agent."""
        info = {}
        for key, cfg in self.agents_config.items():
            info[key] = {
                "role": cfg["role"].strip(),
                "goal": cfg["goal"].strip(),
                "backstory": cfg["backstory"].strip()[:120] + "...",
            }
        return info

    def get_task_info(self) -> dict:
        """Return a summary of each configured task."""
        info = {}
        for key, cfg in self.tasks_config.items():
            info[key] = {
                "description_preview": cfg["description"].strip()[:120] + "...",
                "expected_output_preview": cfg["expected_output"].strip()[:120] + "...",
            }
        return info


# ---------------------------------------------------------------------------
# CLI quick-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("RecruitmentCrew — Crew Assembly Module")
    print("=" * 60)

    try:
        crew = RecruitmentCrew()

        print("\nConfigured Agents:")
        for key, info in crew.get_agent_info().items():
            print(f"\n  [{key.upper()}]")
            print(f"    Role: {info['role']}")
            print(f"    Goal: {info['goal'][:80]}...")

        print("\n\nConfigured Tasks:")
        for key, info in crew.get_task_info().items():
            print(f"\n  [{key}]")
            print(f"    Description: {info['description_preview']}")

        print("\n\nReady for execution. Call crew.kickoff(job_requirements) to start.")

    except FileNotFoundError as exc:
        print(f"\nConfiguration Error: {exc}")
    except Exception as exc:
        print(f"\nError: {exc}")
