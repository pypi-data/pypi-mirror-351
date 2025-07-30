from abc import ABC, abstractmethod
from pathlib import Path

# Abstract base classes for managers, linters, testers

class DependencyManager(ABC):
    """Abstract base class for dependency managers."""
    @abstractmethod
    def init(self, project_path: Path):
        """Initialize/configure the dependency manager in the given project."""
        pass

class PoetryManager(DependencyManager):
    def init(self, project_path: Path):
        pyproject = project_path / "pyproject.toml"
        if not pyproject.exists():
            pyproject.write_text("""[tool.poetry]\nname = 'project'\nversion = '0.1.0'\ndescription = ''\nauthors = []\n""")
        # Optionally, could run 'poetry init' or 'poetry install' here

class PipManager(DependencyManager):
    def init(self, project_path: Path):
        reqs = project_path / "requirements.txt"
        if not reqs.exists():
            reqs.write_text("")

class UvManager(DependencyManager):
    def init(self, project_path: Path):
        # For demonstration, just create a requirements.txt
        reqs = project_path / "requirements.txt"
        if not reqs.exists():
            reqs.write_text("")

class Linter(ABC):
    """Abstract base class for linters."""
    @abstractmethod
    def init(self, project_path: Path):
        """Initialize/configure the linter in the given project."""
        pass

class RuffLinter(Linter):
    def init(self, project_path: Path):
        ruff_config = project_path / "ruff.toml"
        if not ruff_config.exists():
            ruff_config.write_text("[tool.ruff]\nline-length = 88\n")

class PylintLinter(Linter):
    def init(self, project_path: Path):
        pylint_config = project_path / ".pylintrc"
        if not pylint_config.exists():
            pylint_config.write_text("[MASTER]\nignore=tests\n")

class Tester(ABC):
    """Abstract base class for test frameworks."""
    @abstractmethod
    def init(self, project_path: Path):
        """Initialize/configure the test framework in the given project."""
        pass

class PytestTester(Tester):
    def init(self, project_path: Path):
        pytest_ini = project_path / "pytest.ini"
        if not pytest_ini.exists():
            pytest_ini.write_text("[pytest]\naddopts = -ra\n")

class UnittestTester(Tester):
    def init(self, project_path: Path):
        # Unittest does not require config, but we can create a placeholder
        test_dir = project_path / "tests"
        test_dir.mkdir(exist_ok=True)
        (test_dir / "test_sample.py").write_text(
            """import unittest\n\nclass SampleTest(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n\nif __name__ == '__main__':\n    unittest.main()\n""")
