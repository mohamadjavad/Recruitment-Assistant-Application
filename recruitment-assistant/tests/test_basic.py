"""
Recruitment Assistant - Basic Tests

These tests verify the basic project structure and configuration.
"""

import pytest
from pathlib import Path


def test_project_structure():
    """Verify project structure exists."""
    # Check that key directories exist
    assert Path("src/recruitment").exists()
    assert Path("src/recruitment/config").exists()
    assert Path("src/recruitment/tools").exists()
    assert Path("tests").exists()


def test_configuration_files():
    """Verify configuration files exist."""
    config_dir = Path("src/recruitment/config")
    assert (config_dir / "agents.yaml").exists()
    assert (config_dir / "tasks.yaml").exists()


def test_environment_file():
    """Verify environment file exists."""
    assert Path(".env.example").exists()


def test_pyproject_toml():
    """Verify pyproject.toml exists."""
    assert Path("pyproject.toml").exists()


def test_readme():
    """Verify README exists."""
    assert Path("README.md").exists()


def test_imports():
    """Verify basic imports work."""
    import recruitment
    assert hasattr(recruitment, "__version__")
    assert recruitment.__version__ == "0.1.0"