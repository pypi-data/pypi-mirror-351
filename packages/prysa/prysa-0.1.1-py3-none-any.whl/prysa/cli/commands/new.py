import typer
from prysa.scaffolder import scaffold_project
from prysa.tools.managers import get_manager
from prysa.tools.linters import get_linter
from prysa.tools.testers import get_tester

app = typer.Typer()

@app.command()
def new(
    project_name: str = typer.Argument(..., help="Project name"),
    manager: str = typer.Option("poetry", help="Project management tool (poetry, pip, uv)"),
    linter: str = typer.Option("ruff", help="Linter (ruff, pylint)"),
    tester: str = typer.Option("pytest", help="Test framework (pytest, unittest)"),
    no_install: bool = typer.Option(False, help="Do not install dependencies."),
    force: bool = typer.Option(False, help="Overwrite existing files if present."),
    author: str = typer.Option(None, help="Author name."),
    license: str = typer.Option("MIT", help="License type."),
    desc: str = typer.Option("", help="Project description."),
):
    """Scaffold a new Python library project."""
    try:
        project_path = scaffold_project(
            project_name=project_name,
            author=author,
            license_type=license,
            description=desc,
            force=force,
        )
        # Dependency manager integration
        try:
            dep_manager = get_manager(manager)
            dep_manager.init(project_path)
        except Exception as e:
            typer.echo(f"[WARN] Dependency manager setup failed: {e}")
        # Linter integration
        try:
            linter_obj = get_linter(linter)
            linter_obj.init(project_path)
        except Exception as e:
            typer.echo(f"[WARN] Linter setup failed: {e}")
        # Tester integration
        try:
            tester_obj = get_tester(tester)
            tester_obj.init(project_path)
        except Exception as e:
            typer.echo(f"[WARN] Tester setup failed: {e}")
        typer.echo(f"Scaffolded project {project_name} with manager={manager}, linter={linter}, tester={tester}")
    except FileExistsError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
