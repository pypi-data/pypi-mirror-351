import os
from pathlib import Path
import tempfile

def scaffold_project(
    project_name: str,
    author: str = None,
    license_type: str = "MIT",
    description: str = "",
    force: bool = False,
    base_dir: str = None,
):
    """
    Scaffold a new Python library project with standard structure.
    Creates src/, tests/, README.md, LICENSE, and pyproject.toml if not present.
    By default, creates the project in a secure temporary directory (best practice for CLI tools).
    """
    if base_dir is None:
        # Use a secure temp directory in the user's home or system temp dir
        base_dir = tempfile.mkdtemp(prefix="prysa_")
    project_path = Path(base_dir) / project_name
    if project_path.exists() and not force:
        raise FileExistsError(f"Directory '{project_path}' already exists. Use --force to overwrite.")
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "src").mkdir(exist_ok=True)
    (project_path / "tests").mkdir(exist_ok=True)
    # README
    readme = project_path / "README.md"
    if not readme.exists() or force:
        readme.write_text(f"# {project_name}\n\n{description}\n")
    # LICENSE
    license_file = project_path / "LICENSE"
    if not license_file.exists() or force:
        license_file.write_text(f"{license_type} License\n")
    # pyproject.toml (minimal)
    pyproject = project_path / "pyproject.toml"
    if not pyproject.exists() or force:
        pyproject.write_text(f"[project]\nname = '{project_name}'\ndescription = '{description}'\nauthors = ['{author or ''}']\nlicense = '{license_type}'\n")
    return project_path
