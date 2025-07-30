<!-- Logo -->
<p align="center">
  <img src="https://i.imgur.com/enT0B4e.png" alt="prysa logo" width="20%"/>
</p>

**prysa** is a modern Python CLI tool that helps you quickly scaffold and configure new Python library projects with best practices and essential tools. It is designed for ease of use, flexibility, and extensibility, making it the perfect starting point for your next Python library.

## Features
- 📦 **Project Initialization**: Scaffold a new Python library project with a standard structure (`src/`, `tests/`, `README.md`, etc.).
- 🛠️ **Tool Selection**: Choose your preferred dependency manager (Poetry, pip, or uv), linter (Ruff or Pylint), and test framework (Pytest or Unittest).
- ⚡ **Automatic Config Generation**: Instantly generate configuration files for your selected tools.
- 🧩 **Extensible**: Easily add support for new tools by implementing simple abstractions **or by writing plugins**.
- 🔌 **Plugin System**: Discover and load external tools or features via a plugin extension system. Write your own plugins or use community ones!
- 🏗️ **CLI Simplicity**: Minimal, intuitive commands with sensible defaults.

## Quick Start

### Installation

> **Note:** prysa uses [Poetry](https://python-poetry.org/) for dependency management. Make sure you have Poetry installed:
>
> ```bash
> curl -sSL https://install.python-poetry.org | python3 -
> ```

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/prysa.git
cd prysa
poetry install
```

### Usage

Create a new Python library project with a specific dependency manager:

```bash
poetry run prysa new mylib --manager pip
```

This will create a folder `mylib/` with:
- `src/` and `tests/` directories
- `README.md`, `LICENSE`, and a minimal `pyproject.toml` or `requirements.txt` (depending on manager)

Supported managers:
- Poetry (default): creates `pyproject.toml`
- pip: creates `requirements.txt`
- uv: creates `requirements.txt`

You can specify author, license, and description:

```bash
poetry run prysa new mylib --author "Jane Doe" --license MIT --desc "A test library"
```

If the directory exists, use `--force` to overwrite:

```bash
poetry run prysa new mylib --force
```

Create a new project and specify tools:

```bash
poetry run prysa new mylib --manager poetry --linter ruff --tester pytest
```

Add a linter to an existing project:

```bash
poetry run prysa add linter pylint
```

List available tools:

```bash
poetry run prysa list-tools
```

Show help:

```bash
poetry run prysa --help
```

## Command Reference

- `new <project_name>`: Scaffold a new Python library project.
- `add <category> <tool>`: Add a new tool (linter, manager, tester) to an existing project.
- `remove <category> <tool>`: Remove a tool from the project configuration.
- `list-tools`: List all available tools for each category.
- `show-config`: Display the current project configuration and selected tools.
- `help [command]`: Show help message and usage instructions.
- `version`: Show the current version of prysa.

## CLI Design

prysa uses the [Typer](https://typer.tiangolo.com/) library for its CLI. Each command is implemented in its own module for clarity and maintainability. The CLI is easily extensible by adding new command modules and registering them in the main entrypoint.

Example CLI entrypoint (simplified):

```python
import typer
from prysa.cli.commands import new, add, remove, list_tools, show_config

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
```

## Why prysa?
- **Fast**: Get started in seconds with a single command.
- **Flexible**: Choose the tools that fit your workflow.
- **Extensible**: Add new tools and commands as your needs grow.
- **Best Practices**: Start every project with a solid foundation.

## Testing

This project uses [pytest](https://pytest.org/) and [Typer's testing utilities](https://typer.tiangolo.com/tutorial/testing/) to ensure all CLI commands and integrations work as expected.

Run all tests with:

```bash
poetry run pytest
```

Unit tests cover:
- CLI commands
- Project scaffolding
- Dependency manager integration

## Contributing
Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) (to be created) for guidelines.

## License
[MIT License](LICENSE)

---

*prysa is inspired by the needs of modern Python developers who want to focus on building, not boilerplate.*

## Linter Integration

prysa supports modular linter integration. You can specify your preferred linter when creating a project:

```bash
poetry run prysa new mylib --linter ruff
poetry run prysa new mylib --linter pylint
```

This will generate the appropriate configuration file (`ruff.toml` or `.pylintrc`) in your project directory.

Supported linters:
- Ruff (default): creates `ruff.toml`
- Pylint: creates `.pylintrc`

You can also add or remove linters in existing projects:

```bash
poetry run prysa add linter pylint
poetry run prysa remove linter ruff
```

To view available linters:

```bash
poetry run prysa list-tools
```

And to show the current configuration:

```bash
poetry run prysa show-config
```

For help on linter commands:

```bash
poetry run prysa help linter
```

## Plugin Extension System

prysa supports a plugin extension system that allows you to add new tools (managers, linters, testers, etc.) or features without modifying the core codebase.

- Plugins are Python packages that implement the `PrysaPlugin` interface and register themselves with prysa.
- Plugins can be discovered automatically if installed in your environment and named with the `prysa_plugins` namespace (e.g., `prysa_plugins.myplugin`).
- To write a plugin, subclass `PrysaPlugin` and implement the `register()` method.

**Example plugin skeleton:**
```python
from prysa.core.plugins import PrysaPlugin, plugin_registry

class MyCustomManager(PrysaPlugin):
    name = "my_manager"
    type = "manager"
    def register(self):
        # Register with prysa's manager registry here
        pass

plugin_registry.register(MyCustomManager())
```

**Plugin discovery:**
- prysa will automatically discover and load plugins in the `prysa_plugins` namespace when started.
- You can also call `discover_plugins()` from `prysa.core.plugins` to force plugin discovery.

See `tests/test_plugins.py` for example plugin tests.
