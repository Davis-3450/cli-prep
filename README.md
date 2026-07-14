# uv-cli-template

A modern template for creating installable CLI tools with Python using UV package manager.

This provides with some basic structure, tools and conventions to get you started.

It also works as a cheat-sheet!

## Features

- 🚀 Modern Python packaging with UV
- 🎯 Multiple CLI framework examples (Typer, Click, Fire, etc.)
- [ ] 🔍 Code quality with ruff and pre-commit
- 📦 Ready-to-install package structure
- 🔧 Development tools configured

## Quick Start

we will often refer to the app as `uv-cli-template` change it to your own name.

click `use this template` to create a new repo.

1. **Customize your project**:
   - Change `name` in `pyproject.toml` to your CLI tool name
   - Update the package name in `src/` directory (optional)
2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Develop!**

4. **Install your CLI tool locally**:
   ```bash
   uv tool install .
   uv uninstall your-cli-name # remove the tool
   ```

## Development

```bash
# Install with development dependencies
uv sync --group dev

```

## CLI Framework Examples

The template includes examples for popular CLI frameworks in `src/package/main.py`:

- **Typer** (recommended) - Modern, intuitive CLI framework
- **Click** - Composable command line toolkit
- **Argparse** - Built-in argument parser
- **Fire** - Generate CLIs automatically
- **Rich** - Rich text and beautiful formatting
- **Docopt** - Command-line interface from docstrings

Choose one and uncomment the relevant code block, links to the docs are provided.

## Configuration

Update `pyproject.toml`:

```toml
[project]
name = "your-cli-name"  # Change this to your name
# ... other settings

[project.scripts]
your-cli-name = "package.main:app"  # Change entry point
```
## To-Dos

- [ ] Build system
- [ ] Tests
- [ ] Dev tools
- [ ] Pre-commit hooks
- [ ] PyPI publishing
- [ ] Linting and formatting

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV Tools Guide](https://docs.astral.sh/uv/concepts/tools/)
- [Python Packaging Guide](https://packaging.python.org/)

## Contributing

Contributions are welcome! Please feel free to submit a pull request :3
