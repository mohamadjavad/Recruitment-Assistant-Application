"""
Recruitment Assistant - Unit Tests

Comprehensive unit tests for individual functions and components.
Tests focus on behavior, not implementation details.

Covers (PRD §7.5, F-040):
- Input validation logic (main.py)
- YAML config loading (crew.py)
- Agent creation with tool assignment
- Task creation with variable interpolation
- Report formatting and file saving
- Tool availability checks
- Error handling paths
- Legacy tool classes
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

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
    """Return a minimal valid job description."""
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
def crew_instance():
    """Create a RecruitmentCrew instance for testing."""
    from recruitment.crew import RecruitmentCrew
    return RecruitmentCrew()


# ===========================================================================
# 1. Input Validation Logic — main.py
# ===========================================================================

class TestValidateJobDescription:
    """Unit tests for validate_job_description function."""

    def test_returns_empty_list_for_valid_input(self, sample_job_desc):
        """Valid input should return zero errors."""
        from recruitment.main import validate_job_description
        errors = validate_job_description(sample_job_desc)
        assert errors == []

    def test_returns_empty_list_for_minimal_valid_input(self, minimal_job_desc):
        """Minimal valid input should return zero errors."""
        from recruitment.main import validate_job_description
        errors = validate_job_description(minimal_job_desc)
        assert errors == []

    # --- Missing required fields ---

    def test_missing_title(self):
        """Missing title field should return error."""
        from recruitment.main import validate_job_description
        desc = {"description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("title" in e.lower() for e in errors)

    def test_empty_title(self):
        """Empty string title should return error."""
        from recruitment.main import validate_job_description
        desc = {"title": "", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("title" in e.lower() for e in errors)

    def test_missing_description(self):
        """Missing description field should return error."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("description" in e.lower() for e in errors)

    def test_empty_description(self):
        """Empty string description should return error."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "", "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("description" in e.lower() for e in errors)

    def test_missing_responsibilities(self):
        """Missing responsibilities field should return error."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("responsibilities" in e.lower() for e in errors)

    def test_missing_qualifications(self):
        """Missing qualifications field should return error."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("qualifications" in e.lower() for e in errors)

    # --- Minimum length constraints ---

    def test_description_under_100_chars(self):
        """Description under 100 chars should fail."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "Short", "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("100 characters" in e for e in errors)

    def test_description_exactly_100_chars(self):
        """Description exactly 100 chars should pass."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert not any("100 characters" in e for e in errors)

    def test_description_99_chars(self):
        """Description 99 chars should fail."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 99, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("100 characters" in e for e in errors)

    def test_fewer_than_3_responsibilities(self):
        """Fewer than 3 responsibilities should fail."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert any("3 responsibilities" in e for e in errors)

    def test_exactly_3_responsibilities(self):
        """Exactly 3 responsibilities should pass."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert not any("responsibilities" in e.lower() for e in errors)

    def test_fewer_than_3_qualifications(self):
        """Fewer than 3 qualifications should fail."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b"]}
        errors = validate_job_description(desc)
        assert any("3 qualifications" in e for e in errors)

    def test_exactly_3_qualifications(self):
        """Exactly 3 qualifications should pass."""
        from recruitment.main import validate_job_description
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors = validate_job_description(desc)
        assert not any("qualifications" in e.lower() for e in errors)

    def test_empty_dict_all_errors(self):
        """Empty dict should produce at least 4 errors (all required fields)."""
        from recruitment.main import validate_job_description
        errors = validate_job_description({})
        assert len(errors) >= 4

    def test_multiple_errors_compound(self):
        """Multiple issues should produce multiple errors."""
        from recruitment.main import validate_job_description
        errors = validate_job_description({"title": "X"})
        assert len(errors) >= 3  # missing description, responsibilities, qualifications


# ===========================================================================
# 2. Format Job Requirements — main.py
# ===========================================================================

class TestFormatJobRequirementsUnit:
    """Unit tests for format_job_requirements function."""

    def test_returns_string(self, sample_job_desc):
        """Should return a string."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert isinstance(result, str)

    def test_contains_title(self, sample_job_desc):
        """Should contain job title."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Job Title: Senior Python Developer" in result

    def test_contains_description_section(self, sample_job_desc):
        """Should contain description section."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Job Description:" in result

    def test_contains_responsibilities_section(self, sample_job_desc):
        """Should contain responsibilities section."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Key Responsibilities:" in result

    def test_contains_qualifications_section(self, sample_job_desc):
        """Should contain qualifications section."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Required Qualifications:" in result

    def test_contains_numbered_responsibilities(self, sample_job_desc):
        """Responsibilities should be numbered."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "1. Develop and maintain" in result
        assert "5. Contribute to architectural" in result

    def test_contains_numbered_qualifications(self, sample_job_desc):
        """Qualifications should be numbered."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "1. 5+ years" in result

    def test_contains_preferred_qualifications(self, sample_job_desc):
        """Should include preferred qualifications when present."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Preferred Qualifications:" in result
        assert "Docker" in result

    def test_contains_perks(self, sample_job_desc):
        """Should include perks when present."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "Perks and Benefits:" in result
        assert "Remote-first" in result

    def test_no_preferred_when_absent(self, minimal_job_desc):
        """Should not include preferred section when absent."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(minimal_job_desc)
        assert "Preferred Qualifications:" not in result

    def test_no_perks_when_absent(self, minimal_job_desc):
        """Should not include perks section when absent."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(minimal_job_desc)
        assert "Perks and Benefits:" not in result

    def test_empty_responsibilities_list(self):
        """Empty responsibilities list should still produce section header."""
        from recruitment.main import format_job_requirements
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": [], "qualifications": ["a", "b", "c"]}
        result = format_job_requirements(desc)
        assert "Key Responsibilities:" in result

    def test_empty_qualifications_list(self):
        """Empty qualifications list should still produce section header."""
        from recruitment.main import format_job_requirements
        desc = {"title": "Dev", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": []}
        result = format_job_requirements(desc)
        assert "Required Qualifications:" in result

    def test_description_preserved(self, sample_job_desc):
        """Description content should be preserved verbatim."""
        from recruitment.main import format_job_requirements
        result = format_job_requirements(sample_job_desc)
        assert "experienced Python developer" in result


# ===========================================================================
# 3. YAML Config Loading — crew.py
# ===========================================================================

class TestYAMLConfigLoading:
    """Unit tests for YAML configuration loading."""

    def test_load_valid_agents_config(self, crew_instance):
        """Should load agents.yaml successfully."""
        assert crew_instance.agents_config is not None
        assert isinstance(crew_instance.agents_config, dict)

    def test_load_valid_tasks_config(self, crew_instance):
        """Should load tasks.yaml successfully."""
        assert crew_instance.tasks_config is not None
        assert isinstance(crew_instance.tasks_config, dict)

    def test_agents_config_has_all_keys(self, crew_instance):
        """agents.yaml should contain all 4 agent keys."""
        expected = {"researcher", "matcher", "communicator", "reporter"}
        assert set(crew_instance.agents_config.keys()) == expected

    def test_tasks_config_has_all_keys(self, crew_instance):
        """tasks.yaml should contain all 4 task keys."""
        expected = {
            "research_candidates_task",
            "match_and_score_candidates_task",
            "outreach_strategy_task",
            "report_candidates_task",
        }
        assert set(crew_instance.tasks_config.keys()) == expected

    def test_agents_config_roles_are_strings(self, crew_instance):
        """All agent roles should be non-empty strings."""
        for key, cfg in crew_instance.agents_config.items():
            assert isinstance(cfg["role"], str)
            assert cfg["role"].strip()

    def test_agents_config_goals_are_strings(self, crew_instance):
        """All agent goals should be non-empty strings."""
        for key, cfg in crew_instance.agents_config.items():
            assert isinstance(cfg["goal"], str)
            assert cfg["goal"].strip()

    def test_agents_config_backstories_are_strings(self, crew_instance):
        """All agent backstories should be non-empty strings."""
        for key, cfg in crew_instance.agents_config.items():
            assert isinstance(cfg["backstory"], str)
            assert cfg["backstory"].strip()

    def test_tasks_config_descriptions_are_strings(self, crew_instance):
        """All task descriptions should be non-empty strings."""
        for key, cfg in crew_instance.tasks_config.items():
            assert isinstance(cfg["description"], str)
            assert cfg["description"].strip()

    def test_tasks_config_expected_output_are_strings(self, crew_instance):
        """All task expected_output should be non-empty strings."""
        for key, cfg in crew_instance.tasks_config.items():
            assert isinstance(cfg["expected_output"], str)
            assert cfg["expected_output"].strip()

    def test_missing_config_file_raises_error(self, tmp_path):
        """Missing config directory should raise FileNotFoundError."""
        from recruitment.crew import RecruitmentCrew
        with pytest.raises(FileNotFoundError):
            RecruitmentCrew(config_dir=tmp_path / "nonexistent")

    def test_empty_agents_yaml_raises_error(self, tmp_path):
        """Empty agents.yaml should raise ValueError."""
        from recruitment.crew import RecruitmentCrew
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text("")
        (config_dir / "tasks.yaml").write_text("test:\n  description: Test\n  expected_output: Test\n")
        with pytest.raises(ValueError, match="empty"):
            RecruitmentCrew(config_dir=config_dir)

    def test_empty_tasks_yaml_raises_error(self, tmp_path):
        """Empty tasks.yaml should raise ValueError."""
        from recruitment.crew import RecruitmentCrew
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text("agent:\n  role: R\n  goal: G\n  backstory: B\n")
        (config_dir / "tasks.yaml").write_text("")
        with pytest.raises(ValueError, match="empty"):
            RecruitmentCrew(config_dir=config_dir)

    def test_custom_config_dir(self, tmp_path):
        """Should load from custom config directory."""
        from recruitment.crew import RecruitmentCrew
        config_dir = tmp_path / "custom_config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text("myagent:\n  role: Test\n  goal: Test\n  backstory: Test\n")
        (config_dir / "tasks.yaml").write_text("mytask:\n  description: Test {job_requirements}\n  expected_output: Test\n")
        crew = RecruitmentCrew(config_dir=config_dir)
        assert "myagent" in crew.agents_config
        assert "mytask" in crew.tasks_config


# ===========================================================================
# 4. Agent Creation — crew.py
# ===========================================================================

class TestAgentCreationUnit:
    """Unit tests for agent creation from config."""

    def test_creates_correct_count(self, crew_instance):
        """Should create exactly 4 agents."""
        agents = crew_instance._create_agents()
        assert len(agents) == 4

    def test_agents_have_roles(self, crew_instance):
        """Each agent should have a non-empty role."""
        agents = crew_instance._create_agents()
        for agent in agents:
            assert agent.role
            assert isinstance(agent.role, str)

    def test_agents_have_goals(self, crew_instance):
        """Each agent should have a non-empty goal."""
        agents = crew_instance._create_agents()
        for agent in agents:
            assert agent.goal
            assert isinstance(agent.goal, str)

    def test_agents_have_backstories(self, crew_instance):
        """Each agent should have a non-empty backstory."""
        agents = crew_instance._create_agents()
        for agent in agents:
            assert agent.backstory
            assert isinstance(agent.backstory, str)

    def test_reporter_has_no_tools(self, crew_instance):
        """Reporter agent should have no tools (synthesis only per PRD §4.1)."""
        agents = crew_instance._create_agents()
        agent_keys = list(crew_instance.agents_config.keys())
        reporter_idx = agent_keys.index("reporter")
        assert agents[reporter_idx].tools == []

    def test_researcher_may_have_tools(self, crew_instance):
        """Researcher agent should have tools list (may be empty if API keys missing)."""
        agents = crew_instance._create_agents()
        agent_keys = list(crew_instance.agents_config.keys())
        researcher_idx = agent_keys.index("researcher")
        assert isinstance(agents[researcher_idx].tools, list)

    def test_all_agents_verbose(self, crew_instance):
        """All agents should have verbose=True."""
        agents = crew_instance._create_agents()
        for agent in agents:
            assert agent.verbose is True

    def test_all_agents_no_delegation(self, crew_instance):
        """All agents should have allow_delegation=False."""
        agents = crew_instance._create_agents()
        for agent in agents:
            assert agent.allow_delegation is False


# ===========================================================================
# 5. Task Creation — crew.py
# ===========================================================================

class TestTaskCreationUnit:
    """Unit tests for task creation from config."""

    def test_creates_correct_count(self, crew_instance):
        """Should create exactly 4 tasks."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        assert len(tasks) == 4

    def test_first_task_no_context(self, crew_instance):
        """First task should have no context."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        assert tasks[0].context is None

    def test_second_task_has_first_as_context(self, crew_instance):
        """Second task should have exactly one context task."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        assert tasks[1].context is not None
        assert len(tasks[1].context) == 1

    def test_third_task_has_two_contexts(self, crew_instance):
        """Third task should have two context tasks."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        assert len(tasks[2].context) == 2

    def test_fourth_task_has_three_contexts(self, crew_instance):
        """Fourth task should have three context tasks."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        assert len(tasks[3].context) == 3

    def test_variable_interpolation_in_first_3_tasks(self, crew_instance):
        """First 3 tasks should have job_requirements interpolated."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Senior Dev")
        for task in tasks[:3]:
            assert "Senior Dev" in task.description

    def test_reporter_task_uses_context(self, crew_instance):
        """Reporter task description should exist and be non-empty."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        assert tasks[3].description
        assert len(tasks[3].description) > 0

    def test_tasks_have_expected_output(self, crew_instance):
        """All tasks should have expected_output set."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        for task in tasks:
            assert task.expected_output
            assert isinstance(task.expected_output, str)

    def test_tasks_assigned_to_correct_agents(self, crew_instance):
        """Each task should be assigned to the correct agent."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        agent_keys = list(crew_instance.agents_config.keys())
        # Verify tasks are assigned in order: researcher, matcher, communicator, reporter
        for i, task in enumerate(tasks):
            assert task.agent is agents[i]

    def test_invalid_task_key_raises_error(self, crew_instance):
        """Task with unmapped agent key should raise ValueError."""
        from recruitment.crew import RecruitmentCrew
        import yaml
        # Create config with unknown task
        config_dir = crew_instance.config_dir
        # Temporarily modify tasks config
        original_tasks = crew_instance.tasks_config.copy()
        crew_instance.tasks_config["unknown_task"] = {
            "description": "Test {job_requirements}",
            "expected_output": "Test",
        }
        agents = crew_instance._create_agents()
        with pytest.raises(ValueError, match="agent mapping"):
            crew_instance._create_tasks(agents, "Job Title: Test")
        crew_instance.tasks_config = original_tasks


# ===========================================================================
# 6. Crew Assembly — crew.py
# ===========================================================================

class TestCrewAssemblyUnit:
    """Unit tests for crew assembly."""

    def test_assemble_crew(self, crew_instance):
        """Should assemble a valid Crew."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        crew = crew_instance._create_crew(agents, tasks)
        assert crew is not None
        assert hasattr(crew, "kickoff")

    def test_crew_has_all_agents(self, crew_instance):
        """Crew should contain all 4 agents."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        crew = crew_instance._create_crew(agents, tasks)
        assert len(crew.agents) == 4

    def test_crew_has_all_tasks(self, crew_instance):
        """Crew should contain all 4 tasks."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        crew = crew_instance._create_crew(agents, tasks)
        assert len(crew.tasks) == 4

    def test_crew_process_is_sequential(self, crew_instance):
        """Crew process should be sequential (PRD §4.1)."""
        from crewai import Process
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        crew = crew_instance._create_crew(agents, tasks)
        assert crew.process == Process.sequential

    def test_crew_verbose_enabled(self, crew_instance):
        """Crew should have verbose logging enabled (PRD §5.3)."""
        agents = crew_instance._create_agents()
        tasks = crew_instance._create_tasks(agents, "Job Title: Test")
        crew = crew_instance._create_crew(agents, tasks)
        assert crew.verbose is True


# ===========================================================================
# 7. Tool Availability & Factory — custom_tools.py
# ===========================================================================

class TestToolAvailabilityUnit:
    """Unit tests for tool availability checks."""

    def test_serper_check_returns_bool(self):
        """check_tool_availability('serper') should return bool."""
        from recruitment.tools.custom_tools import check_tool_availability
        result = check_tool_availability("serper")
        assert isinstance(result, bool)

    def test_scrape_check_returns_bool(self):
        """check_tool_availability('scrape') should return bool."""
        from recruitment.tools.custom_tools import check_tool_availability
        result = check_tool_availability("scrape")
        assert isinstance(result, bool)

    def test_unknown_tool_returns_false(self):
        """Unknown tool name should return False."""
        from recruitment.tools.custom_tools import check_tool_availability
        assert check_tool_availability("unknown_tool") is False

    def test_serper_unavailable_without_api_key(self):
        """SerperDevTool should be unavailable without SERPER_API_KEY."""
        from recruitment.tools.custom_tools import check_tool_availability
        with patch.dict(os.environ, {"SERPER_API_KEY": ""}, clear=False):
            # Remove SERPER_API_KEY if present
            env = os.environ.copy()
            env.pop("SERPER_API_KEY", None)
            with patch.dict(os.environ, env, clear=True):
                result = check_tool_availability("serper")
                assert result is False

    def test_get_tools_for_reporter_returns_empty(self):
        """Reporter agent should get no tools."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("reporter")
        assert tools == []

    def test_get_tools_for_researcher_returns_list(self):
        """Researcher agent should get a list (possibly empty)."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("researcher")
        assert isinstance(tools, list)

    def test_get_tools_for_matcher_returns_list(self):
        """Matcher agent should get a list (possibly empty)."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("matcher")
        assert isinstance(tools, list)

    def test_get_tools_for_communicator_returns_list(self):
        """Communicator agent should get a list (possibly empty)."""
        from recruitment.tools.custom_tools import get_tools_for_agent
        tools = get_tools_for_agent("communicator")
        assert isinstance(tools, list)


# ===========================================================================
# 8. Retry Decorator — custom_tools.py
# ===========================================================================

class TestRetryDecoratorUnit:
    """Unit tests for retry_with_backoff decorator."""

    def test_success_on_first_attempt(self):
        """Should return result on first successful attempt."""
        from recruitment.tools.custom_tools import retry_with_backoff

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def succeed():
            return 42

        assert succeed() == 42

    def test_success_after_retries(self):
        """Should succeed after transient failures."""
        from recruitment.tools.custom_tools import retry_with_backoff
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("transient")
            return "ok"

        assert fail_then_succeed() == "ok"
        assert call_count == 3

    def test_raises_after_max_retries(self):
        """Should raise after exhausting all retries."""
        from recruitment.tools.custom_tools import retry_with_backoff

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fail():
            raise RuntimeError("permanent")

        with pytest.raises(RuntimeError, match="permanent"):
            always_fail()

    def test_preserves_function_name(self):
        """Decorator should preserve original function name."""
        from recruitment.tools.custom_tools import retry_with_backoff

        @retry_with_backoff(max_retries=1, base_delay=0.01)
        def my_function():
            pass

        assert my_function.__name__ == "my_function"

    def test_only_catches_specified_exceptions(self):
        """Should only catch specified exception types."""
        from recruitment.tools.custom_tools import retry_with_backoff

        @retry_with_backoff(max_retries=3, base_delay=0.01, exceptions=(ValueError,))
        def raise_type_error():
            raise TypeError("not caught")

        with pytest.raises(TypeError):
            raise_type_error()

    def test_zero_retries_means_no_retry(self):
        """With max_retries=0, should not retry at all."""
        from recruitment.tools.custom_tools import retry_with_backoff
        call_count = 0

        @retry_with_backoff(max_retries=0, base_delay=0.01)
        def fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            fail()
        assert call_count == 1


# ===========================================================================
# 9. Legacy Tool Classes — custom_tools.py
# ===========================================================================

class TestLegacyToolClasses:
    """Unit tests for legacy tool classes."""

    def test_candidate_search_tool_init(self):
        """CandidateSearchTool should initialize."""
        from recruitment.tools.custom_tools import CandidateSearchTool
        tool = CandidateSearchTool()
        assert tool.name == "CandidateSearchTool"
        assert tool.description

    def test_candidate_scoring_tool_init(self):
        """CandidateScoringTool should initialize."""
        from recruitment.tools.custom_tools import CandidateScoringTool
        tool = CandidateScoringTool()
        assert tool.name == "CandidateScoringTool"
        assert tool.description

    def test_outreach_template_tool_init(self):
        """OutreachTemplateTool should initialize."""
        from recruitment.tools.custom_tools import OutreachTemplateTool
        tool = OutreachTemplateTool()
        assert tool.name == "OutreachTemplateTool"
        assert tool.description

    def test_scoring_tool_returns_structure(self):
        """CandidateScoringTool.score_candidate should return valid structure."""
        from recruitment.tools.custom_tools import CandidateScoringTool
        tool = CandidateScoringTool()
        result = tool.score_candidate({"id": "123"}, "Job: Dev")
        assert "candidate_id" in result
        assert "dimensions" in result
        assert "overall_score" in result
        assert "justification" in result
        assert result["candidate_id"] == "123"

    def test_scoring_tool_default_candidate_id(self):
        """CandidateScoringTool should default to 'unknown' for missing id."""
        from recruitment.tools.custom_tools import CandidateScoringTool
        tool = CandidateScoringTool()
        result = tool.score_candidate({}, "Job: Dev")
        assert result["candidate_id"] == "unknown"

    def test_outreach_tool_returns_structure(self):
        """OutreachTemplateTool.generate_template should return valid structure."""
        from recruitment.tools.custom_tools import OutreachTemplateTool
        tool = OutreachTemplateTool()
        result = tool.generate_template({"id": "456"}, "Job: Dev")
        assert "candidate_id" in result
        assert "initial_contact" in result
        assert "follow_up_sequence" in result
        assert "interview_invitation" in result
        assert "personalization_tokens" in result
        assert result["candidate_id"] == "456"

    def test_outreach_tool_default_candidate_id(self):
        """OutreachTemplateTool should default to 'unknown' for missing id."""
        from recruitment.tools.custom_tools import OutreachTemplateTool
        tool = OutreachTemplateTool()
        result = tool.generate_template({}, "Job: Dev")
        assert result["candidate_id"] == "unknown"

    def test_tool_registry_has_all_tools(self):
        """TOOL_REGISTRY should contain all 3 tool classes."""
        from recruitment.tools.custom_tools import TOOL_REGISTRY
        assert "candidate_search" in TOOL_REGISTRY
        assert "candidate_scoring" in TOOL_REGISTRY
        assert "outreach_template" in TOOL_REGISTRY

    def test_get_tool_valid_name(self):
        """get_tool should return instance for valid name."""
        from recruitment.tools.custom_tools import get_tool
        tool = get_tool("candidate_scoring")
        assert tool is not None
        assert hasattr(tool, "score_candidate")

    def test_get_tool_invalid_name_raises(self):
        """get_tool should raise ValueError for unknown tool."""
        from recruitment.tools.custom_tools import get_tool
        with pytest.raises(ValueError, match="Tool not found"):
            get_tool("nonexistent_tool")


# ===========================================================================
# 10. Introspection Helpers — crew.py
# ===========================================================================

class TestIntrospectionHelpers:
    """Unit tests for crew introspection methods."""

    def test_get_agent_info(self, crew_instance):
        """get_agent_info should return all agents."""
        info = crew_instance.get_agent_info()
        assert len(info) == 4
        assert "researcher" in info
        assert "matcher" in info
        assert "communicator" in info
        assert "reporter" in info

    def test_get_agent_info_has_required_fields(self, crew_instance):
        """Each agent info should have role, goal, and backstory."""
        info = crew_instance.get_agent_info()
        for key, details in info.items():
            assert "role" in details
            assert "goal" in details
            assert "backstory" in details

    def test_get_agent_info_backstory_truncated(self, crew_instance):
        """Agent backstory should be truncated with ellipsis."""
        info = crew_instance.get_agent_info()
        for key, details in info.items():
            assert details["backstory"].endswith("...")

    def test_get_task_info(self, crew_instance):
        """get_task_info should return all tasks."""
        info = crew_instance.get_task_info()
        assert len(info) == 4
        assert "research_candidates_task" in info
        assert "match_and_score_candidates_task" in info
        assert "outreach_strategy_task" in info
        assert "report_candidates_task" in info

    def test_get_task_info_has_required_fields(self, crew_instance):
        """Each task info should have description_preview and expected_output_preview."""
        info = crew_instance.get_task_info()
        for key, details in info.items():
            assert "description_preview" in details
            assert "expected_output_preview" in details

    def test_get_task_info_previews_truncated(self, crew_instance):
        """Task previews should be truncated with ellipsis."""
        info = crew_instance.get_task_info()
        for key, details in info.items():
            assert details["description_preview"].endswith("...")
            assert details["expected_output_preview"].endswith("...")


# ===========================================================================
# 11. Kickoff Input Validation — crew.py
# ===========================================================================

class TestKickoffInputValidation:
    """Unit tests for kickoff method input validation."""

    def test_empty_string_raises_value_error(self, crew_instance):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            crew_instance.kickoff("")

    def test_whitespace_only_raises_value_error(self, crew_instance):
        """Whitespace-only string should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            crew_instance.kickoff("   \n\t  ")

    def test_none_raises_error(self, crew_instance):
        """None input should raise an error."""
        with pytest.raises((ValueError, AttributeError)):
            crew_instance.kickoff(None)


# ===========================================================================
# 12. ValidationError Exception — main.py
# ===========================================================================

class TestValidationError:
    """Unit tests for ValidationError exception."""

    def test_is_exception_subclass(self):
        """ValidationError should be a subclass of Exception."""
        from recruitment.main import ValidationError
        assert issubclass(ValidationError, Exception)

    def test_can_be_raised(self):
        """ValidationError should be raiseable."""
        from recruitment.main import ValidationError
        with pytest.raises(ValidationError):
            raise ValidationError("test error")

    def test_can_be_caught(self):
        """ValidationError should be catchable as Exception."""
        from recruitment.main import ValidationError
        try:
            raise ValidationError("test")
        except Exception as e:
            assert isinstance(e, ValidationError)
            assert str(e) == "test"
