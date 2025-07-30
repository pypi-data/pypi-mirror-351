import typer
from prysa.cli.commands import new, add, remove, list_tools, show_config
from prysa.core.plugins import discover_plugins

# Discover and register plugins at CLI startup
try:
    discover_plugins()
except Exception as e:
    # Optionally log or print a warning, but don't block CLI startup
    pass

app = typer.Typer(help="prysa: Python project quickstart tool")

app.command()(new.new)
app.command()(add.add)
app.command()(remove.remove)
app.command()(list_tools.list_tools)
app.command()(show_config.show_config)

@app.command()
def version():
    """Show the current version of prysa."""
    import importlib.metadata
    try:
        v = importlib.metadata.version("prysa")
    except importlib.metadata.PackageNotFoundError:
        v = "(local)"
    typer.echo(f"prysa version: {v}")

if __name__ == "__main__":
    app()
