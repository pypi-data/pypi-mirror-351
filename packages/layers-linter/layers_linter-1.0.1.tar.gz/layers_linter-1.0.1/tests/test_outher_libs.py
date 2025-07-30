# File: tests/test_layer_linter.py
import pytest

from src.layers_linter.analyzer import analyze_dependencies
from src.layers_linter.config import load_config


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure with the given config."""

    def create_project(toml_config: str, project_structure: dict):
        # Create config file
        config_path = tmp_path / "deps.toml"
        with open(config_path, "w") as f:
            f.write(toml_config)

        # Create project files
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        for file_path, content in project_structure.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

        return config_path

    return create_project


def test_valid_dependency(temp_project):
    toml_config = """
exclude_modules = []

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]

[layers.presentation]
contains_modules = ["project.presentation.*"]

[layers.helpers]
contains_modules = ["project.helpers.*"]

[libs]
[libs.sqlalchemy]
upstream = ["infrastructure"]

[libs.pydantic]
upstream = ["helpers"]

[libs.fastapi]
upstream = ["presentation"]

[libs.argparse]
upstream = ["presentation"]
"""

    project_structure = {
        "domain/service.py": """from project.infrastructure.db import Database""",
        "infrastructure/db.py": """
# This is allowed to depend on domain
from project.domain.service import Service
import sqlalchemy
        """,
        "helpers/validator.py": """import pydantic""",
        "presentation/controller.py": """
import argparse
import fastapi
        """,
    }

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, [])

    assert len(problems) == 0


def test_invalid_library_usage(temp_project):
    toml_config = """
exclude_modules = []

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]

[libs]
[libs.sqlalchemy]
upstream = ["infrastructure"]
"""

    project_structure = {"domain/service.py": """import sqlalchemy"""}

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, [])

    assert len(problems) == 1
    problem = problems[0]
    assert problem.code == "LA020"
