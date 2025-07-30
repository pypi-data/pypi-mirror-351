from pathlib import Path
import toml

class ConfigManager:
    """Manages project configuration files in an idempotent way."""
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)

    def read_pyproject(self):
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            return toml.load(pyproject)
        return {}

    def write_pyproject(self, data: dict):
        pyproject = self.project_path / "pyproject.toml"
        toml.dump(data, pyproject.open("w"))

    def update_pyproject(self, section: str, values: dict):
        data = self.read_pyproject()
        data.setdefault(section, {}).update(values)
        self.write_pyproject(data)

    def show_config(self):
        """Return a string summary of the current project configuration."""
        summary = []
        pyproject = self.read_pyproject()
        summary.append("[pyproject.toml]")
        summary.append(toml.dumps(pyproject) if pyproject else "Not found.")
        for fname in ["requirements.txt", "ruff.toml", ".pylintrc", "pytest.ini"]:
            f = self.project_path / fname
            if f.exists():
                summary.append(f"\n[{fname}]\n{f.read_text()}")
        return "\n".join(summary)
