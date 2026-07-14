# contain all your deps inside /package

# app() is your entry point for convenience (we can use any name tho)


# -------------
# Typer (https://typer.tiangolo.com/) | Recommended
# uv add typer
# -------------
# import typer
# app = typer.Typer()
# @app.command()
# def hello():
#     typer.echo("Hello, World!")
#
# if __name__ == "__main__":
#     app()

# -------------
# Argparse (https://docs.python.org/3/library/argparse.html)
# built-in
# -------------
# import argparse
# def app():
#   parser = argparse.ArgumentParser()
#   parser.add_argument("--name", type=str, default="World")
#   args = parser.parse_args()
#   print(f"Hello, {args.name}!")
#
# if __name__ == "__main__":
#   app()

# -------------
# Click (https://click.palletsprojects.com/)
# uv add click
# -------------
# import click
# @click.command()
# @click.option("--name", default="World")
# def app(name: str):
#     click.echo(f"Hello, {name}!")
#
# if __name__ == "__main__":
#     app()

# -------------
# Fire (https://github.com/google/python-fire)
# uv add fire
# -------------
# import fire
# def greet(name="World"):
#     return f"Hello, {name}!"
#
# def app():
#     fire.Fire(greet)
#
# if __name__ == "__main__":
#     app()

# -------------
# Rich CLI (https://rich.readthedocs.io/en/stable/introduction.html)
# uv add rich
# -------------
# from rich.console import Console
# import argparse
# def app():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--name", default="World")
#     args = parser.parse_args()
#     console = Console()
#     console.print(f"[bold green]Hello, {args.name}![/]")
#
# if __name__ == "__main__":
#     app()

# -------------
# Docopt (http://docopt.org/)
# uv add docopt
# -------------
# """Usage:
#   app.py [--name=<name>]
#
# Options:
#   -h --help        Show this help.
#   --name=<name>    Your name [default: World].
# """
# from docopt import docopt
# def app():
#     args = docopt(__doc__)
#     print(f"Hello, {args['--name']}!")
#
# if __name__ == "__main__":
#     app()


# heres an example with typer:
import typer

app = typer.Typer(
    name="uv-cli-template",
    help="A modern CLI template built with UV and Typer 🚀",
    add_completion=False,
)


@app.command()
def hello(world: str = "Hello World") -> None:
    typer.secho("Hello World", fg=typer.colors.RED, bold=True)
    typer.secho(world, fg=typer.colors.GREEN, bold=True)
    typer.secho(world, fg=typer.colors.BLUE, bold=True)
    typer.secho(world, fg=typer.colors.YELLOW, bold=True)
    typer.secho(world, fg=typer.colors.MAGENTA, bold=True)
    typer.secho(world, fg=typer.colors.CYAN, bold=True)
    typer.secho(world, fg=typer.colors.WHITE, bold=True)
    typer.secho(world, fg=typer.colors.BLACK, bold=True)


@app.command()
def version() -> None:
    """Show version information."""
    typer.secho("template 0.1.0", fg=typer.colors.BLUE, bold=True)
    typer.secho("Made with love! :3", fg=typer.colors.CYAN)


@app.command()
def config() -> None:
    """Show configuration information."""
    typer.secho("Configuration:", fg=typer.colors.YELLOW, bold=True)


if __name__ == "__main__":
    app()
