"""Entry point for cli-prep: a TUI to practise multiple-choice quizzes."""

from __future__ import annotations

from pathlib import Path

import typer

from .models import Quiz, QuizError, discover_quizzes
from .session import Session
from .tui import PrepApp

app = typer.Typer(
    name="prep",
    help="Practise multiple-choice quizzes in a terminal UI.",
    add_completion=False,
    no_args_is_help=False,
)


def _default_quizzes_dir() -> Path:
    """Find a quizzes directory: ./quizzes, else the one bundled in the repo."""
    cwd = Path.cwd() / "quizzes"
    if cwd.is_dir():
        return cwd
    repo = Path(__file__).resolve().parents[2] / "quizzes"
    return repo


@app.command()
def start(
    quiz: Path | None = typer.Argument(
        None, help="Quiz JSON file to open. Omit to pick from a menu."
    ),
    quizzes_dir: Path = typer.Option(
        None,
        "--quizzes-dir",
        "-d",
        help="Directory to scan for quizzes (default: ./quizzes).",
    ),
) -> None:
    """Launch the quiz TUI (default command)."""
    directory = quizzes_dir or _default_quizzes_dir()
    PrepApp(quizzes_dir=directory, quiz_path=quiz).run()


@app.command("list")
def list_quizzes(
    quizzes_dir: Path = typer.Option(
        None, "--quizzes-dir", "-d", help="Directory to scan for quizzes."
    ),
) -> None:
    """List available quizzes and any saved progress."""
    directory = quizzes_dir or _default_quizzes_dir()
    quizzes = discover_quizzes(directory)
    if not quizzes:
        typer.secho(f"No quizzes found in {directory}", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    for path in quizzes:
        session = Session.load(path)
        if session and session.completed:
            status = typer.style("completed", fg=typer.colors.GREEN)
        elif session and session.has_progress:
            status = typer.style(
                f"in progress {session.index}/{session.num_questions}",
                fg=typer.colors.YELLOW,
            )
        else:
            status = typer.style("new", fg=typer.colors.BLUE)
        typer.echo(f"  {path.stem:<24} {status}")


@app.command()
def reset(
    quiz: Path = typer.Argument(..., help="Quiz JSON file to reset progress for."),
) -> None:
    """Delete saved progress for a quiz."""
    try:
        loaded = Quiz.load(quiz)
    except QuizError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(1)
    Session.for_quiz(loaded).reset()
    typer.secho(f"Progress reset for {loaded.title}", fg=typer.colors.GREEN)


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context) -> None:
    """Run the TUI menu when called with no subcommand."""
    if ctx.invoked_subcommand is None:
        directory = _default_quizzes_dir()
        PrepApp(quizzes_dir=directory, quiz_path=None).run()


if __name__ == "__main__":
    app()
