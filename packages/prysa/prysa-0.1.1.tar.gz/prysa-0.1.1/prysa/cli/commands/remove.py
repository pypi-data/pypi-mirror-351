import typer

app = typer.Typer()

@app.command()
def remove(
    category: str = typer.Argument(..., help="Tool category: manager, linter, tester"),
    tool: str = typer.Argument(..., help="Tool name to remove"),
):
    """Remove a tool from the project configuration."""
    typer.echo(f"Removed {tool} from category {category}")
    # TODO: Call logic to remove tool
