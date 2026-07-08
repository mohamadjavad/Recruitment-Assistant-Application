"""
Recruitment Assistant - Edge Case Tests

Tests for unusual, boundary, and stress conditions.
Validates robustness of the system under non-standard inputs.

Covers:
- Very long job descriptions
- Special characters in input
- Unicode characters
- Empty optional fields
- Maximum item counts
- Boundary conditions
- Error message quality
"""

import os
import sys
import pytest
from pathlib import Path

# Ensure src is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def crew_instance():
    """Create a RecruitmentCrew instance for testing."""
    from recruitment.crew import RecruitmentCrew
    return RecruitmentCrew()


# ===========================================================================
# 1. Very Long Job Descriptions
# ===========================================================================

class TestLongDescriptions:
    """Tests for very long job descriptions."""

    def test_very_long_description(self):
        """Description with 10,000 characters should pass validation."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 10000,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_very_long_title(self):
        """Title with 1,000 characters should pass validation."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "D" * 1000,
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_many_responsibilities(self):
        """50 responsibilities should pass validation."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": [f"Responsibility {i}" for i in range(50)],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_many_qualifications(self):
        """50 qualifications should pass validation."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": [f"Qualification {i}" for i in range(50)],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_long_description_formats_correctly(self):
        """Long description should format without errors."""
        from recruitment.main import format_job_requirements
        desc = {
            "title": "Senior Engineer",
            "description": "A" * 5000,
            "responsibilities": ["Lead team", "Design architecture", "Mentor juniors"],
            "qualifications": ["10+ years experience", "CS degree", "Strong communication"],
        }
        result = format_job_requirements(desc)
        assert "Senior Engineer" in result
        assert "A" * 100 in result  # First 100 chars preserved


# ===========================================================================
# 2. Special Characters
# ===========================================================================

class TestSpecialCharacters:
    """Tests for special characters in input."""

    def test_special_chars_in_title(self):
        """Title with special characters should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "C++ / Python Developer (Senior)",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_special_chars_in_description(self):
        """Description with special characters should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "Looking for a developer with experience in C++, Python, & JavaScript. Must know HTML/CSS & be familiar with REST APIs (JSON/XML). Salary: $100k-$150k. " + "x" * 50,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_newlines_in_description(self):
        """Description with newlines should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "Line one\nLine two\nLine three\n" + "x" * 90,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_html_in_description(self):
        """Description with HTML tags should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "<p>We are looking for a <strong>senior</strong> developer</p> with experience in <em>Python</em> and Django frameworks. " + "x" * 40,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_quotes_in_responsibilities(self):
        """Responsibilities with quotes should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": [
                'Write "clean" code',
                "Use 'best practices'",
                "Follow the team's standards",
            ],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_special_chars_format_correctly(self):
        """Special characters should be preserved in formatted output."""
        from recruitment.main import format_job_requirements
        desc = {
            "title": "C++ Developer",
            "description": "Looking for C++ & Python developer. Salary: $100k-$150k. " + "x" * 60,
            "responsibilities": ['Write "clean" code', "Use 'best' practices", "Follow team's standards"],
            "qualifications": ["C++ (5+ yrs)", "Python (3+ yrs)", "Git/CI-CD"],
        }
        result = format_job_requirements(desc)
        assert "C++ Developer" in result
        assert "$100k-$150k" in result
        assert '"clean"' in result


# ===========================================================================
# 3. Unicode Characters
# ===========================================================================

class TestUnicode:
    """Tests for Unicode characters in input."""

    def test_unicode_in_title(self):
        """Title with accented characters should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Développeur Python Senior — Überingenieur",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_unicode_in_description(self):
        """Description with Unicode should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "We are looking for a developer experienced in 日本語 (Japanese) markets. Knowledge of émojis 🎉 and special chars ñ, ü, ö is a plus. " + "x" * 40,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_cjk_characters(self):
        """CJK characters should pass validation."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "开发工程师",
            "description": "我们需要一位有经验的Python开发工程师。要求熟悉Django框架，有良好的团队合作精神和沟通能力。" + "x" * 60,
            "responsibilities": ["编写代码", "参与代码审查", "编写文档"],
            "qualifications": ["Python经验", "Django经验", "团队合作"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_emoji_in_text(self):
        """Emojis in text should pass validation."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev 🚀",
            "description": "Join our team! 🎉 We offer great benefits 💰 and growth opportunities 📈. " + "x" * 50,
            "responsibilities": ["Code", "Test", "Deploy 🚀"],
            "qualifications": ["Python 🐍", "Django", "Git"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_mixed_scripts(self):
        """Mixed scripts (Latin + Cyrillic + Arabic) should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Developer (Разработчик)",
            "description": "Looking for a developer proficient in Python and JavaScript. مرحبا and Добро пожаловать to our team. " + "x" * 40,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []


# ===========================================================================
# 4. Empty Optional Fields
# ===========================================================================

class TestEmptyOptionalFields:
    """Tests for optional fields being empty or absent."""

    def test_no_preferred_qualifications(self):
        """Missing preferred_qualifications should be valid."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_empty_preferred_qualifications(self):
        """Empty preferred_qualifications list should be valid."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
            "preferred_qualifications": [],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_no_perks(self):
        """Missing perks should be valid."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_empty_perks(self):
        """Empty perks list should be valid."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
            "perks": [],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_both_optional_empty(self):
        """Both optional fields empty should be valid."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
            "preferred_qualifications": [],
            "perks": [],
        }
        errors = validate_job_description(desc)
        assert errors == []

    def test_format_without_optional_sections(self):
        """Formatting without optional fields should omit sections."""
        from recruitment.main import format_job_requirements
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        result = format_job_requirements(desc)
        assert "Preferred Qualifications:" not in result
        assert "Perks and Benefits:" not in result


# ===========================================================================
# 5. Boundary Conditions
# ===========================================================================

class TestBoundaryConditions:
    """Tests for boundary conditions."""

    def test_exactly_minimum_responsibilities(self):
        """Exactly 3 responsibilities should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert not any("responsibilities" in e.lower() for e in errors)

    def test_exactly_minimum_qualifications(self):
        """Exactly 3 qualifications should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert not any("qualifications" in e.lower() for e in errors)

    def test_one_responsibility_short(self):
        """2 responsibilities should fail."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert any("3 responsibilities" in e for e in errors)

    def test_one_qualification_short(self):
        """2 qualifications should fail."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b"],
        }
        errors = validate_job_description(desc)
        assert any("3 qualifications" in e for e in errors)

    def test_description_exactly_boundary(self):
        """Description exactly 100 chars should pass."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "a" * 100,
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        assert errors == []


# ===========================================================================
# 6. Configuration Edge Cases
# ===========================================================================

class TestConfigEdgeCases:
    """Tests for configuration edge cases."""

    def test_agents_yaml_with_extra_fields(self, tmp_path):
        """Extra fields in agents.yaml should not break loading."""
        from recruitment.crew import RecruitmentCrew
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text(
            "agent1:\n  role: Test\n  goal: Test\n  backstory: Test\n  extra_field: ignored\n"
        )
        (config_dir / "tasks.yaml").write_text(
            "task1:\n  description: Test {job_requirements}\n  expected_output: Test\n"
        )
        crew = RecruitmentCrew(config_dir=config_dir)
        assert "agent1" in crew.agents_config

    def test_tasks_yaml_with_extra_fields(self, tmp_path):
        """Extra fields in tasks.yaml should not break loading."""
        from recruitment.crew import RecruitmentCrew
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text(
            "agent1:\n  role: Test\n  goal: Test\n  backstory: Test\n"
        )
        (config_dir / "tasks.yaml").write_text(
            "task1:\n  description: Test {job_requirements}\n  expected_output: Test\n  extra_field: ignored\n"
        )
        crew = RecruitmentCrew(config_dir=config_dir)
        assert "task1" in crew.tasks_config

    def test_single_agent_single_task(self, tmp_path):
        """Single agent and task should work."""
        from recruitment.crew import RecruitmentCrew
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text(
            "sole_agent:\n  role: Sole Agent\n  goal: Do everything\n  backstory: Jack of all trades\n"
        )
        (config_dir / "tasks.yaml").write_text(
            "sole_task:\n  description: Do the thing {job_requirements}\n  expected_output: Thing done\n"
        )
        crew = RecruitmentCrew(config_dir=config_dir)
        assert len(crew.agents_config) == 1
        assert len(crew.tasks_config) == 1

    def test_yaml_with_multiline_strings(self, tmp_path):
        """YAML multiline strings should load correctly."""
        from recruitment.crew import RecruitmentCrew
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "agents.yaml").write_text(
            "agent1:\n  role: |\n    Multi\n    Line\n    Role\n  goal: >-\n    Single goal\n  backstory: Plain string\n"
        )
        (config_dir / "tasks.yaml").write_text(
            "task1:\n  description: >-\n    Multi line\n    description {job_requirements}\n  expected_output: Output\n"
        )
        crew = RecruitmentCrew(config_dir=config_dir)
        assert "agent1" in crew.agents_config


# ===========================================================================
# 7. Task Variable Interpolation Edge Cases
# ===========================================================================

class TestTaskInterpolationEdgeCases:
    """Tests for variable interpolation in task descriptions."""

    def test_special_chars_in_requirements(self, crew_instance):
        """Special characters in job requirements should interpolate safely."""
        agents = crew_instance._create_agents()
        job_reqs = "Title: Dev\nDesc: C++ & Python (senior)\nSalary: $100k-$150k"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        for task in tasks[:3]:
            assert "C++ & Python" in task.description

    def test_newlines_in_requirements(self, crew_instance):
        """Newlines in job requirements should be preserved."""
        agents = crew_instance._create_agents()
        job_reqs = "Title: Dev\n\nDescription:\nLine 1\nLine 2"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        assert "Line 1" in tasks[0].description
        assert "Line 2" in tasks[0].description

    def test_unicode_in_requirements(self, crew_instance):
        """Unicode in job requirements should interpolate safely."""
        agents = crew_instance._create_agents()
        job_reqs = "Title: 開発者\nDescription: 日本語のジョブ"
        tasks = crew_instance._create_tasks(agents, job_reqs)
        assert "開発者" in tasks[0].description

    def test_very_long_requirements(self, crew_instance):
        """Very long job requirements should interpolate."""
        agents = crew_instance._create_agents()
        job_reqs = "Title: Dev\nDescription: " + "A" * 10000
        tasks = crew_instance._create_tasks(agents, job_reqs)
        assert "A" * 100 in tasks[0].description


# ===========================================================================
# 8. Display Functions — main.py
# ===========================================================================

class TestDisplayFunctions:
    """Tests for display/utility functions in main.py."""

    def test_display_error_with_suggestion(self, capsys):
        """display_error should show error and suggestion."""
        from recruitment.main import display_error
        display_error("Something went wrong", "Try restarting")
        captured = capsys.readouterr()
        assert "Something went wrong" in captured.out

    def test_display_error_without_suggestion(self, capsys):
        """display_error should work without suggestion."""
        from recruitment.main import display_error
        display_error("Something went wrong")
        captured = capsys.readouterr()
        assert "Something went wrong" in captured.out

    def test_display_workflow_start(self, capsys):
        """display_workflow_start should print start message."""
        from recruitment.main import display_workflow_start
        display_workflow_start()
        captured = capsys.readouterr()
        assert "Starting Recruitment Workflow" in captured.out

    def test_display_workflow_complete(self, capsys):
        """display_workflow_complete should print completion message."""
        from recruitment.main import display_workflow_complete
        display_workflow_complete("/path/to/report.md", 125.5)
        captured = capsys.readouterr()
        assert "Workflow Complete" in captured.out

    def test_display_report(self, capsys):
        """display_report should print report content."""
        from recruitment.main import display_report
        display_report("/path/report.md", "# Test Report\nContent here")
        captured = capsys.readouterr()
        assert "Candidate Report Generated" in captured.out


# ===========================================================================
# 9. Concurrent Access Patterns
# ===========================================================================

class TestConcurrentPatterns:
    """Tests for concurrent access patterns (MVP: single-user)."""

    def test_multiple_crew_instances_independent(self):
        """Multiple RecruitmentCrew instances should be independent."""
        from recruitment.crew import RecruitmentCrew
        crew1 = RecruitmentCrew()
        crew2 = RecruitmentCrew()
        assert crew1.config_dir == crew2.config_dir
        # Verify they are independent objects
        assert crew1 is not crew2
        # Configs should be equal (same content) but separate objects (YAML loads fresh each time)
        assert crew1.agents_config == crew2.agents_config
        assert crew1.tasks_config == crew2.tasks_config

    def test_multiple_validation_calls(self):
        """Multiple validation calls should be independent."""
        from recruitment.main import validate_job_description
        desc1 = {"title": "Dev1", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        desc2 = {"title": "", "description": "x" * 100, "responsibilities": ["a", "b", "c"], "qualifications": ["a", "b", "c"]}
        errors1 = validate_job_description(desc1)
        errors2 = validate_job_description(desc2)
        assert errors1 == []
        assert len(errors2) > 0


# ===========================================================================
# 10. Error Message Quality
# ===========================================================================

class TestErrorMessages:
    """Tests for error message quality and actionability."""

    def test_missing_field_error_is_descriptive(self):
        """Validation error should clearly identify missing field."""
        from recruitment.main import validate_job_description
        errors = validate_job_description({})
        # Should mention specific field names
        error_text = " ".join(errors)
        assert "title" in error_text.lower()
        assert "description" in error_text.lower()
        assert "responsibilities" in error_text.lower()
        assert "qualifications" in error_text.lower()

    def test_length_error_includes_current_count(self):
        """Length errors should include current count."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "Short",
            "responsibilities": ["a", "b", "c"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        desc_errors = [e for e in errors if "100 characters" in e]
        assert len(desc_errors) == 1
        assert "5 characters" in desc_errors[0]  # Current count

    def test_count_error_includes_current_count(self):
        """Count errors should include current count."""
        from recruitment.main import validate_job_description
        desc = {
            "title": "Dev",
            "description": "x" * 100,
            "responsibilities": ["a", "b"],
            "qualifications": ["a", "b", "c"],
        }
        errors = validate_job_description(desc)
        resp_errors = [e for e in errors if "responsibilities" in e.lower()]
        assert len(resp_errors) == 1
        assert "2" in resp_errors[0]  # Current count

    def test_value_error_includes_config_path(self):
        """FileNotFoundError should include config path."""
        from recruitment.crew import RecruitmentCrew
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            RecruitmentCrew(config_dir=Path("/nonexistent/path"))
