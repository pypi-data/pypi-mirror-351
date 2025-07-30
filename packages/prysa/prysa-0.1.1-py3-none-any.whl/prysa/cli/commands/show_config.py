import typer
from pathlib import Path
from prysa.config.config_manager import ConfigManager

app = typer.Typer()

@app.command()
def show_config(project_path: str = typer.Argument('.', help="Project directory")):
    """Display the current project configuration and selected tools."""
    typer.echo("Current project configuration:\n")
    cm = ConfigManager(Path(project_path))
    typer.echo(cm.show_config())
