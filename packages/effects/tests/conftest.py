"""Pytest fixtures for layered-effects tests."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_effects_yaml():
    """Sample minimal effects.yaml content."""
    return """
version: "1.0"
parameter_types: {}
effects:
  test_effect:
    description: "Test effect"
    command: 'echo "test"'
composites: {}
presets: {}
"""


@pytest.fixture
def package_effects_file(tmp_path: Path, sample_effects_yaml: str):
    """Create a package effects.yaml file."""
    effects_file = tmp_path / "package_effects.yaml"
    effects_file.write_text(sample_effects_yaml)
    return effects_file


@pytest.fixture
def project_effects_file(tmp_path: Path):
    """Create a project effects.yaml file."""
    effects_file = tmp_path / "project_effects.yaml"
    content = """
version: "1.0"
parameter_types: {}
effects:
  project_effect:
    description: "Project effect"
    command: 'echo "project"'
composites: {}
presets: {}
"""
    effects_file.write_text(content)
    return effects_file


@pytest.fixture
def user_effects_file(tmp_path: Path):
    """Create a user effects.yaml file."""
    effects_file = tmp_path / "user_effects.yaml"
    content = """
version: "1.0"
effects:
  user_effect:
    description: "User effect"
    command: 'echo "user"'
"""
    effects_file.write_text(content)
    return effects_file
