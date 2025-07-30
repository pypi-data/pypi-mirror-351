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


def test_invalid_dependency(temp_project):
    toml_config = """
exclude_modules = []

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]
upstream = []
downstream = ["infrastructure"]

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]
upstream = ["domain"]
downstream = []
"""

    project_structure = {
        "domain/service.py": """from project.infrastructure.db import Database""",
        "infrastructure/db.py": """from project.domain.service import Service""",
    }

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, [])

    assert len(problems) == 1
    assert problems[0].layer_to == "domain"
    assert problems[0].layer_from == "infrastructure"


def test_valid_dependency_downstream(temp_project):
    toml_config = """
exclude_modules = []

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]
upstream = []
downstream = ["infrastructure"]

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]
upstream = []
downstream = []
"""

    project_structure = {
        "domain/service.py": """from project.infrastructure.db import Database""",
        "infrastructure/db.py": """pass""",
    }

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, [])

    assert len(problems) == 1
    assert problems[0].layer_to == "infrastructure"
    assert problems[0].layer_from == "domain"


def test_valid_dependency_upstream(temp_project):
    toml_config = """
exclude_modules = []

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]
upstream = []
downstream = []

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]
upstream = ["domain"]
downstream = []
"""

    project_structure = {
        "domain/service.py": """from project.infrastructure.db import Database""",
        "infrastructure/db.py": """pass""",
    }

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, [])

    assert len(problems) == 1


def test_type_checking_import(temp_project):
    toml_config = """
exclude_modules = []

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]
upstream = []
downstream = ["infrastructure"]

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]
upstream = ["domain"]
downstream = []
    """

    project_structure = {
        "domain/service.py": """
if TYPE_CHECKING:
    from project.infrastructure.db import Database
""",
        "infrastructure/db.py": """
if TYPE_CHECKING:
    from project.domain.service import Service
""",
    }

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, [])

    assert len(problems) == 0


def test_exclude_modules(temp_project):
    toml_config = """
exclude_modules = ["*.db"]

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]
upstream = []
downstream = ["infrastructure"]

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]
upstream = ["domain"]
downstream = []
    """

    project_structure = {
        "domain/service.py": """from project.infrastructure.db import Database""",
        "infrastructure/db.py": """from project.domain.service import Service""",
    }

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, exclude_modules)

    assert len(problems) == 0


def test_invalid_dependency2(temp_project):
    toml_config = """
exclude_modules = []

[layers]
[layers.domain]
contains_modules = ["project.domain.*"]
upstream = []
downstream = []

[layers.infrastructure]
contains_modules = ["project.infrastructure.*"]
upstream = []
downstream = []
"""

    project_structure = {
        "domain/service.py": """from project.infrastructure.db import Database""",
        "infrastructure/db.py": """from project.domain.service import Service""",
    }

    config_path = temp_project(toml_config, project_structure)
    layers, libs, exclude_modules = load_config(config_path)
    project_root = config_path.parent / "project"
    problems = analyze_dependencies(project_root, layers, libs, [])

    assert len(problems) == 2
