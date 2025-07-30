import typer

app = typer.Typer()

@app.command()
def add(
    category: str = typer.Argument(..., help="Tool category: manager, linter, tester"),
    tool: str = typer.Argument(..., help="Tool name to add"),
    force: bool = typer.Option(False, help="Overwrite existing config if present."),
):
    """Add a new tool to an existing project."""
    typer.echo(f"Added {tool} to category {category} (force={force})")
    # TODO: Call logic to add tool
