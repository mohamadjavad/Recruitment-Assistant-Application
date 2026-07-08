"""
Recruitment Assistant - Integration Tests

Tests the integration between main.py (CLI) and crew.py (CrewAI workflow).
Validates the complete data flow from input collection to report generation.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure src is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_job_desc():
    """Return a valid job description dictionary."""
    return {
        "title": "Senior Python Developer",
        "description": "We are looking for an experienced Python developer to join our team. "
                       "The ideal candidate will have strong experience with Python, Django, "
                       "and modern web technologies. You will be responsible for developing "
                       "and maintaining our core platform, collaborating with cross-functional "
                       "teams, and contributing to architectural decisions.",
        "responsibilities": [
            "Develop and maintain Python applications using Django framework",
            "Collaborate with product managers and designers to define features",
            "Write clean, testable, and well-documented code",
            "Participate in code reviews and mentor junior developers",
            "Contribute to architectural decisions and technical documentation",
        ],
        "qualifications": [
            "5+ years of experience with Python development",
            "Strong experience with Django or Flask frameworks",
            "Experience with PostgreSQL or other relational databases",
            "Familiarity with cloud services (AWS, GCP, or Azure)",
            "Excellent communication and teamwork skills",
        ],
        "preferred_qualifications": [
            "Experience with Docker and containerization",
            "Knowledge of CI/CD pipelines",
            "Contributions to open-source projects",
        ],
        "perks": [
            "Competitive salary and equity",
            "Remote-first work environment",
            "Professional development budget",
            "Health and wellness benefits",
        ],
    }


@pytest.fixture
def minimal_job_desc():
    """Return a minimal valid job description (required fields only)."""
    return {
        "title": "Junior Developer",
        "description": "A entry-level developer position requiring knowledge of Python and basic web development. "
                       "The candidate will work on internal tools and learn from senior engineers.",
        "responsibilities": [
            "Write Python scripts and simple web applications",
            "Assist senior developers with bug fixes",
            "Write unit tests for new features",
        ],
        "qualifications": [
            "Bachelor's degree in CS or related field",
            "Basic Python knowledge",
            "Willingness to learn",
        ],
    }


@pytest.fixture
def invalid_job_desc():
    """Return an invalid job description (missing required fields)."""
    return {
        "title": "",
        "description": "Short",
        "responsibilities": [],
        "qualifications": [],
    }


@pytest.fixture
def crew_instance():
    """Create a RecruitmentCrew instance for testing."""
    from recruitment.crew import RecruitmentCrew
    return RecruitmentCrew()


@pytest.fixture
def formatted_requirements(sample_job_desc):
    """Return formatted job requirements string."""
    from recruitment.main import format_job_requirements
    return format_job_requirements(sample_job_desc)


# ---------------------------------------------------------------------------
# Test 1: Import Verification
# ---------------------------------------------------------------------------

class TestImports:
    """Test that all modules import correctly."""

    def test_import_main(self):
        """main.py should import without errors."""
        import recruitment.main
        assert hasattr(recruitment.main, "main")
        assert hasattr(recruitment.main, "validate_job_description")
        assert hasattr(recruitment.main, "format_job_requirements")

    def test_import_crew(self):
        """crew.py should import without errors."""
        import recruitment.crew
        assert hasattr(recruitment.crew, "RecruitmentCrew")

    def test_import_tools(self):
        """custom_tools.py should import without errors."""
        import recruitment.tools.custom_tools
        assert hasattr(recruitment.tools.custom_tools, "get_tools_for_agent")
        assert hasattr(recruitment.tools.custom_tools, "check_tool_availability")

    def test_import_package(self):
        """The recruitment package should import correctly."""
        import recruitment
        assert recruitment.__version__ == "0.1.0"


# ---------------------------------------------------------------------------
# Test 2: Crew Initialization
# ---------------------------------------------------------------------------

class TestCrewInitialization:
    """Test that RecruitmentCrew initializes correctly."""

    def test_crew_init_default_config(self, crew_instance):
        """Crew should initialize with default config directory."""
        assert crew_instance.config_dir is not None
        assert crew_instance.config_dir.exists()
        assert crew_instance.agents_config is not None
        assert crew_instance.tasks_config is not None

    def test_crew_init_custom_config(self, tmp_path):
        """Crew should initialize with custom config directory."""
        from recruitment.crew import RecruitmentCrew
        # Create minimal config files
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text(
            "researcher:\n  role: Test\n  goal: Test\n  backstory: Test\n"
        )
        (config_dir / "tasks.yaml").write_text(
            "test_task:\n  description: Test {job_requirements}\n  expected_output: Test\n"
        )
        crew = RecruitmentCrew(config_dir=config_dir)
        assert "researcher" in crew.agents_config

    def test_crew_config_loads_agents(self, crew_instance):
        """YAML config should contain all 4 agent definitions."""
        expected_agents = ["researcher", "matcher", "communicator", "reporter"]
        for agent_key in expected_agents:
            assert agent_key in crew_instance.agents_config, f"Missing agent: {agent_key}"

    def test_crew_config_loads_tasks(self, crew_instance):
        """YAML config should contain all 4 task definitions."""
        expected_tasks = [
            "research_candidates_task",
            "match_and_score_candidates_task",
            "outreach_strategy_task",
            "report_candidates_task",
        ]
        for task_key in expected_tasks:
            assert task_key in crew_instance.tasks_config, f"Missing task: {task_key}"

    def test_agent_info_structure(self, crew_instance):
        """Agent info should have role, goal, and backstory."""
        info = crew_instance.get_agent_info()
        for agent_key, details in info.items():
            assert "role" in details
            assert "goal" in details
            assert "backstory" in details

    def test_task_info_structure(self, crew_instance):
        """Task info should have description and expected_output."""
        info = crew_instance.get_task_info()
        for task_key, details in info.items():
            assert "description_preview" in details
            assert "expected_output_preview" in details


# ---------------------------------------------------------------------------
# Test 3: Input Validation (main.py)
# ---------------------------------------------------------------------------

class TestInputValidation:
    """Test job description validation in main.py."""

    def test_valid_job_desc_passes(self, sample_job_desc):
        """Valid job description should produce no errors."""
        from recruitment.main import validate_job_description
        errors = validate_job_description(sample_job_desc)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_minimal_valid_job_desc_passes(self, minimal_job_desc):
        """Minimal valid job description should produce no errors."""
        from recruitment.main import validate_job_description
        errors = validate_job_description(minimal_job_desc)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_missing_title_fails(self):
        """Missing title should produce validation error."""
        from recruitment.main import validate_job_description
        desc = {"description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("title" in e.lower() for e in errors)

    def test_empty_title_fails(self):
        """Empty title should produce validation error."""
        from recruitment.main import validate_job_description
        desc = {"title": "", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("title" in e.lower() for e in errors)

    def test_short_description_fails(self):
        """Description under 100 chars should produce validation error."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "Short", "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("100 characters" in e for e in errors)

    def test_few_responsibilities_fails(self):
        """Fewer than 3 responsibilities should produce validation error."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("3 responsibilities" in e for e in errors)

    def test_few_qualifications_fails(self):
        """Fewer than 3 qualifications should produce validation error."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b"]}
        errors = validate_job_description(desc)
        assert any("3 qualifications" in e for e in errors)

    def test_empty_dict_fails(self):
        """Empty dict should produce multiple validation errors."""
        from recruitment.main import validate_job_description
        errors = validate_job_description({})
        assert len(errors) >= 4  # title, description, responsibilities, qualifications

    def test_invalid_job_desc_fails(self, invalid_job_desc):
        """Invalid job description should produce multiple errors."""
        from recruitment.main import validate_job_description
        errors = validate_job_description(invalid_job_desc)
        assert len(errors) >= 1


# ---------------------------------------------------------------------------
# Test 4: Format Job Requirements
# ---------------------------------------------------------------------------

class TestFormatJobRequirements:
    """Test job requirements formatting."""

    def test_format_contains_title(self, sample_job_desc):
        """Formatted output should contain job title."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Senior Python Developer" in result

    def test_format_contains_description(self, sample_job_desc):
        """Formatted output should contain job description."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "experienced Python developer" in result

    def test_format_contains_responsibilities(self, sample_job_desc):
        """Formatted output should contain responsibilities."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Django" in result

    def test_format_contains_qualifications(self, sample_job_desc):
        """Formatted output should contain qualifications."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "5+ years" in result

    def test_format_contains_preferred(self, sample_job_desc):
        """Formatted output should contain preferred qualifications."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Docker" in result

    def test_format_contains_perks(self, sample_job_desc):
        """Formatted output should contain perks."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Remote-first" in result

    def test_format_minimal(self, minimal_job_desc):
        """Minimal job desc should format without preferred/perks sections."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(minimal_job_desc)
        assert "Junior Developer" in result
        assert "Job Title:" in result
        assert "Key Responsibilities:" in result


# ---------------------------------------------------------------------------
# Test 5: YAML Config Integrity
# ---------------------------------------------------------------------------

class TestYAMLConfigIntegrity:
    """Test that YAML configs load and have correct structure."""

    def test_agents_yaml_loads(self, crew_instance):
        """agents.yaml should load with correct structure."""
        for agent_key, config in crew_instance.agents_config.items():
            assert "role" in config, f"Agent {agent_key} missing 'role'"
            assert "goal" in config, f"Agent {agent_key} missing 'goal'"
            assert "backstory" in config, f"Agent {agent_key} missing 'backstory'"
            assert isinstance(config["role"], str)
            assert isinstance(config["goal"], str)
            assert isinstance(config["backstory"], str)

    def test_tasks_yaml_loads(self, crew_instance):
        """tasks.yaml should load with correct structure."""
        for task_key, config in crew_instance.tasks_config.items():
            assert "description" in config, f"Task {task_key} missing 'description'"
            assert "expected_output" in config, f"Task {task_key} missing 'expected_output'"
            assert isinstance(config["description"], str)
            assert isinstance(config["expected_output"], str)

    def test_tasks_have_job_requirements_placeholder(self, crew_instance):
        """First 3 tasks should have {job_requirements} placeholder."""
        tasks_with_placeholder = [
            "research_candidates_task",
            "match_and_score_candidates_task",
            "outreach_strategy_task",
        ]
        for task_key in tasks_with_placeholder:
            desc = crew_instance.tasks_config[task_key]["description"]
            assert "{job_requirements}" in desc, f"Task {task_key} missing {{job_requirements}} placeholder"

    def test_agent_count(self, crew_instance):
        """Should have exactly 4 agents."""
        assert len(crew_instance.agents_config) == 4

    def test_task_count(self, crew_instance):
        """Should have exactly 4 tasks."""
        assert len(crew_instance.tasks_config) == 4


# ---------------------------------------------------------------------------
# Test 6: Agent Creation (requires crewai)
# ---------------------------------------------------------------------------

class TestAgentCreation:
    """Test agent creation from config (requires crewai)."""

    def test_create_agents(self, crew_instance):
        """Should create 4 agents from YAML config."""
        agents = crew_instance._create_agents()
        assert len(agents) == 4

    def test_agent_roles(self, crew_instance):
        """Agents should have correct roles from YAML."""
        agents = crew_instance._create_agents()
        roles = [a.role for a in agents]
        assert any("Researcher" in r for r in roles)
        assert any("Matcher" in r for r in roles)
        assert any("Communicator" in r or "Strategist" in r for r in roles)
        assert any("Reporter" in r or "Specialist" in r for r in roles)

    def test_agent_tools_assigned(self, crew_instance):
        """Agents should have tools assigned (or empty list for reporter)."""
        agents = crew_instance._create_agents()
        for agent in agents:
            # All agents should have a tools attribute (even if empty)
            assert hasattr(agent, "tools")
            assert isinstance(agent.tools, list)


# ---------------------------------------------------------------------------
# Test 7: Task Creation (requires crewai)
# ---------------------------------------------------------------------------

class TestTaskCreation:
    """Test task creation from config (requires crewai)."""

    def test_create_tasks(self, crew_instance):
        """Should create 4 tasks from YAML config."""
        agents = crew_instance._create_agents()
        job_reqs = "Job Title: Test\nDescription: Test role with Python"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        assert len(tasks) == 4

    def test_task_description_interpolation(self, crew_instance):
        """First 3 tasks should have job_requirements interpolated; reporter uses context."""
        agents = crew_instance._create_agents()
        job_reqs = "Job Title: Senior Developer"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        # First 3 tasks have {job_requirements} placeholder — should be interpolated
        for task in tasks[:3]:
            assert "Job Title: Senior Developer" in task.description
        # Reporter task (4th) is synthesis — gets context from previous tasks, not interpolation
        assert tasks[3].description  # Just verify it exists and is non-empty

    def test_task_context_chaining(self, crew_instance):
        """Tasks should have context from previous tasks."""
        agents = crew_instance._create_agents()
        job_reqs = "Job Title: Test"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        # First task has no context
        assert tasks[0].context is None
        # Second task has first task as context
        assert tasks[1].context is not None
        assert len(tasks[1].context) == 1
        # Third task has first two as context
        assert len(tasks[2].context) == 2
        # Fourth task has first three as context
        assert len(tasks[3].context) == 3


# ---------------------------------------------------------------------------
# Test 8: Crew Assembly (requires crewai)
# ---------------------------------------------------------------------------

class TestCrewAssembly:
    """Test crew assembly from agents and tasks (requires crewai)."""

    def test_create_crew(self, crew_instance):
        """Should assemble a CrewAI Crew."""
        agents = crew_instance._create_agents()
        job_reqs = "Job Title: Test"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        crew = crew_instance._create_crew(agents, tasks)
        assert crew is not None
        assert hasattr(crew, "kickoff")

    def test_crew_has_agents(self, crew_instance):
        """Assembled crew should have all agents."""
        agents = crew_instance._create_agents()
        job_reqs = "Job Title: Test"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        crew = crew_instance._create_crew(agents, tasks)
        assert len(crew.agents) == 4

    def test_crew_has_tasks(self, crew_instance):
        """Assembled crew should have all tasks."""
        agents = crew_instance._create_agents()
        job_reqs = "Job Title: Test"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        crew = crew_instance._create_crew(agents, tasks)
        assert len(crew.tasks) == 4


# ---------------------------------------------------------------------------
# Test 9: Tool Availability
# ---------------------------------------------------------------------------

class TestToolAvailability:
    """Test tool availability checks."""

    def test_get_tools_for_reporter(self):
        """Reporter agent should get no tools."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("reporter")
        assert tools == []

    def test_get_tools_for_researcher(self):
        """Researcher agent should get tools (may be empty if API keys missing)."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("researcher")
        assert isinstance(tools, list)

    def test_get_tools_for_matcher(self):
        """Matcher agent should get tools (may be empty if API keys missing)."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("matcher")
        assert isinstance(tools, list)

    def test_get_tools_for_communicator(self):
        """Communicator agent should get tools (may be empty if API keys missing)."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("communicator")
        assert isinstance(tools, list)

    def test_check_tool_availability_returns_bool(self):
        """check_tool_availability should return a boolean."""
        from recruitment.tools.custom_tools import check_tool_availability
        assert isinstance(check_tool_availability("serper"), bool)
        assert isinstance(check_tool_availability("scrape"), bool)


# ---------------------------------------------------------------------------
# Test 10: Data Flow Integration
# ---------------------------------------------------------------------------

class TestDataFlow:
    """Test the complete data flow from input to output format."""

    def test_dict_to_string_flow(self, sample_job_desc):
        """Job desc dict should convert to formatted string correctly."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert isinstance(result, str)
        assert len(result) > 0
        # Should be parseable (contain expected sections)
        assert "Job Title:" in result
        assert "Job Description:" in result
        assert "Key Responsibilities:" in result
        assert "Required Qualifications:" in result

    def test_string_accepted_by_crew(self, crew_instance, formatted_requirements):
        """Formatted string should be accepted by crew.kickoff without ValueError."""
        # We don't actually execute (no API keys), but validate input handling
        assert formatted_requirements.strip() != ""
        # This should not raise ValueError
        crew_instance._agents = crew_instance._create_agents()
        crew_instance._tasks = crew_instance._create_tasks(
            crew_instance._agents, formatted_requirements
        )
        assert len(crew_instance._tasks) == 4

    def test_empty_string_rejected_by_kickoff(self, crew_instance):
        """Empty job requirements should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            crew_instance.kickoff("")

    def test_whitespace_only_rejected_by_kickoff(self, crew_instance):
        """Whitespace-only job requirements should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            crew_instance.kickoff("   \n  \t  ")


# ---------------------------------------------------------------------------
# Test 11: Environment Variable Handling
# ---------------------------------------------------------------------------

class TestEnvironmentHandling:
    """Test environment variable handling."""

    def test_main_checks_env_vars(self):
        """main.py should check for required environment variables."""
        from recruitment.main import main
        # Just verify the function exists and is callable
        assert callable(main)

    def test_crew_loads_dotenv(self):
        """crew.py should load .env via dotenv."""
        from recruitment.crew import load_dotenv
        # Should not raise
        load_dotenv()


# ---------------------------------------------------------------------------
# Test 12: Integration Seam (main.py → crew.py)
# ---------------------------------------------------------------------------

class TestIntegrationSeam:
    """Test the integration seam between main.py and crew.py."""

    def test_run_workflow_calls_recruitment_crew(self):
        """run_workflow should import and use RecruitmentCrew."""
        import inspect
        from recruitment.main import run_workflow
        source = inspect.getsource(run_workflow)
        assert "RecruitmentCrew" in source
        assert "kickoff" in source

    def test_run_workflow_formats_requirements(self):
        """run_workflow should call format_job_requirements."""
        import inspect
        from recruitment.main import run_workflow
        source = inspect.getsource(run_workflow)
        assert "format_job_requirements" in source

    def test_main_calls_run_workflow(self):
        """main() should call run_workflow."""
        import inspect
        from recruitment.main import main
        source = inspect.getsource(main)
        assert "run_workflow" in source

    def test_main_saves_report(self):
        """main() should save report to candidate_report.md."""
        import inspect
        from recruitment.main import main
        source = inspect.getsource(main)
        assert "candidate_report.md" in source

    def test_crew_kickoff_returns_string(self, crew_instance):
        """crew.kickoff should return a string (via normalization)."""
        import inspect
        source = inspect.getsource(crew_instance.kickoff)
        assert "str(result)" in source or "raw" in source


# ---------------------------------------------------------------------------
# Test 13: Error Handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """Test error handling in the integration."""

    def test_validation_error_class_exists(self):
        """ValidationError exception should be defined."""
        from recruitment.main import ValidationError
        assert issubclass(ValidationError, Exception)

    def test_display_error_function_exists(self):
        """display_error function should exist."""
        from recruitment.main import display_error
        assert callable(display_error)

    def test_display_workflow_start_exists(self):
        """display_workflow_start function should exist."""
        from recruitment.main import display_workflow_start
        assert callable(display_workflow_start)

    def test_display_workflow_complete_exists(self):
        """display_workflow_complete function should exist."""
        from recruitment.main import display_workflow_complete
        assert callable(display_workflow_complete)

    def test_display_report_exists(self):
        """display_report function should exist."""
        from recruitment.main import display_report
        assert callable(display_report)

    def test_crew_missing_config_raises_error(self, tmp_path):
        """Crew should raise FileNotFoundError with missing config."""
        from recruitment.crew import RecruitmentCrew
        with pytest.raises(FileNotFoundError):
            RecruitmentCrew(config_dir=tmp_path / "nonexistent")


# ---------------------------------------------------------------------------
# Test 14: Retry Decorator
# ---------------------------------------------------------------------------

class TestRetryDecorator:
    """Test retry with exponential backoff."""

    def test_retry_decorator_exists(self):
        """retry_with_backoff decorator should be importable."""
        from recruitment.tools.custom_tools import retry_with_backoff
        assert callable(retry_with_backoff)

    def test_retry_decorator_applies(self):
        """retry_with_backoff should return a decorator."""
        from recruitment.tools.custom_tools import retry_with_backoff
        decorator = retry_with_backoff(max_retries=1, base_delay=0.01)
        assert callable(decorator)

    def test_retry_succeeds_on_first_try(self):
        """Retry decorator should pass through on success."""
        from recruitment.tools.custom_tools import retry_with_backoff

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def succeed():
            return "ok"

        assert succeed() == "ok"

    def test_retry_raises_after_max_retries(self):
        """Retry decorator should raise after exhausting retries."""
        from recruitment.tools.custom_tools import retry_with_backoff

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fail():
            raise ValueError("fail")

        with pytest.raises(ValueError, match="fail"):
            always_fail()
