<!-- Logo -->
<p align="center">
  <img src="https://i.imgur.com/nzALfWF.png" alt="prysa logo" width="20%"/>
</p>

**prysa** is a modern Python CLI tool that helps you quickly scaffold and configure new Python library projects with best practices and essential tools. It is designed for ease of use, flexibility, and extensibility, making it the perfect starting point for your next Python library.

## Features
- 📦 **Project Initialization**: Scaffold a new Python library project with a standard structure (`src/`, `tests/`, `README.md`, etc.).
- 🛠️ **Tool Selection**: Choose your preferred dependency manager (Poetry, pip, or uv), linter (Ruff or Pylint), and test framework (Pytest or Unittest).
- ⚡ **Automatic Config Generation**: Instantly generate configuration files for your selected tools.
- 🧩 **Extensible**: Easily add support for new tools by implementing simple abstractions.
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

Create a new Python library project with default tools:

```bash
prysa new mylib
```

Create a new project and specify tools:

```bash
prysa new mylib --manager poetry --linter ruff --tester pytest
```

Add a linter to an existing project:

```bash
prysa add linter pylint
```

List available tools:

```bash
prysa list-tools
```

Show help:

```bash
prysa help
```

## Command Reference

- `new <project_name>`: Scaffold a new Python library project.
- `add <category> <tool>`: Add a new tool (linter, manager, tester) to an existing project.
- `remove <category> <tool>`: Remove a tool from the project configuration.
- `list-tools`: List all available tools for each category.
- `show-config`: Display the current project configuration and selected tools.
- `help [command]`: Show help message and usage instructions.
- `version`: Show the current version of prysa.

## Why prysa?
- **Fast**: Get started in seconds with a single command.
- **Flexible**: Choose the tools that fit your workflow.
- **Extensible**: Add new tools and commands as your needs grow.
- **Best Practices**: Start every project with a solid foundation.

## Contributing
Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) (to be created) for guidelines.

## License
[MIT License](LICENSE)

---

*prysa is inspired by the needs of modern Python developers who want to focus on building, not boilerplate.*
