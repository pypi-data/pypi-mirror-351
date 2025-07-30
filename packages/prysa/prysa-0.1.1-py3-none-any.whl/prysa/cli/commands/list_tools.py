import typer

app = typer.Typer()

@app.command()
def list_tools():
    """List all available tools for each category."""
    typer.echo("Managers: poetry, pip, uv\nLinters: ruff, pylint\nTesters: pytest, unittest")
    # In the future, this can be made dynamic by querying the registry in tools/managers, tools/linters, tools/testers
