"""Textual TUI for practising quizzes."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Grid, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

from .models import Quiz, QuizError, discover_quizzes
from .session import Session

LETTERS = "ABCDEFGHIJ"


class ConfirmScreen(ModalScreen[bool]):
    """A yes/no modal dialog."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self._message, id="confirm-question"),
            Button("Yes", variant="error", id="yes"),
            Button("No", variant="primary", id="no"),
            id="confirm-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class MenuScreen(Screen):
    """Pick a quiz to practise."""

    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(self, quizzes: list[Path]) -> None:
        super().__init__()
        self._quizzes = quizzes

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Center(Label("Choose a quiz", id="menu-title"))
        items: list[ListItem] = []
        for path in self._quizzes:
            session = Session.load(path)
            if session and session.completed:
                tag = "  [green]✓ completed[/]"
            elif session and session.has_progress:
                done = session.index
                tag = f"  [yellow]▶ resume ({done}/{session.num_questions})[/]"
            else:
                tag = ""
            item = ListItem(Label(f"{path.stem}{tag}"))
            item.quiz_path = path  # type: ignore[attr-defined]
            items.append(item)
        yield VerticalScroll(ListView(*items, id="menu-list"))
        yield Footer()

    def on_mount(self) -> None:
        if self._quizzes:
            self.query_one("#menu-list", ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        path = getattr(event.item, "quiz_path", None)
        if path is not None:
            self.app.open_quiz(path)  # type: ignore[attr-defined]


class QuizScreen(Screen):
    """The main practice screen for a single quiz."""

    BINDINGS = [
        Binding("h", "toggle_hints", "Hints"),
        Binding("r", "reset", "Reset"),
        Binding("n", "next", "Next", show=False),
        Binding("space", "next", "Next"),
        Binding("m", "menu", "Menu"),
        Binding("q", "quit", "Quit"),
        Binding("1", "select(0)", "1", show=False),
        Binding("2", "select(1)", "2", show=False),
        Binding("3", "select(2)", "3", show=False),
        Binding("4", "select(3)", "4", show=False),
        Binding("5", "select(4)", "5", show=False),
    ]

    answered: reactive[bool] = reactive(False)

    def __init__(self, quiz: Quiz, session: Session) -> None:
        super().__init__()
        self.quiz = quiz
        self.session = session

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="stats")
        with VerticalScroll(id="body"):
            yield Static(id="question")
            yield Static(id="hint")
            yield Vertical(id="options")
            yield Static(id="feedback")
        yield Footer()

    async def on_mount(self) -> None:
        # Resume where we left off, clamping to a valid range.
        if self.session.index >= len(self.quiz):
            self.session.index = len(self.quiz) - 1
        await self.load_question()

    # ---- rendering ---------------------------------------------------

    @property
    def current(self):
        return self.quiz.questions[self.session.index]

    async def load_question(self) -> None:
        q = self.current
        previous = self.session.answers.get(self.session.index)
        self.answered = previous is not None

        number = self.session.index + 1
        self.query_one("#question", Static).update(
            f"[b]Question {number}/{len(self.quiz)}[/]\n\n{q.question}"
        )

        hint_widget = self.query_one("#hint", Static)
        if self.session.hints_enabled and not self.answered:
            hint_widget.update(f"[dim italic]💡 {q.hint}[/]")
            hint_widget.display = True
        else:
            hint_widget.display = False

        options_box = self.query_one("#options", Vertical)
        await options_box.remove_children()
        buttons = []
        for i, option in enumerate(q.options):
            letter = LETTERS[i] if i < len(LETTERS) else str(i + 1)
            btn = Button(f"{letter}. {option}", id=f"opt-{i}", classes="option")
            buttons.append(btn)
        await options_box.mount(*buttons)

        feedback = self.query_one("#feedback", Static)
        if self.answered and previous is not None:
            self._reveal(previous)
        else:
            feedback.update("")
            feedback.display = False

        self.update_stats()

    def _reveal(self, choice: int) -> None:
        q = self.current
        correct_index = q.answer_index
        for i in range(len(q.options)):
            btn = self.query_one(f"#opt-{i}", Button)
            btn.disabled = True
            if i == correct_index:
                btn.variant = "success"
            elif i == choice:
                btn.variant = "error"

        feedback = self.query_one("#feedback", Static)
        verdict = (
            "[b green]✓ Correct![/]"
            if choice == correct_index
            else "[b red]✗ Incorrect[/]"
        )
        last = "  [dim](space/n → results)[/]" if self._is_last() else "  [dim](space/n → next)[/]"
        feedback.update(f"{verdict}\n\n[b]Why:[/] {q.explanation}{last}")
        feedback.display = True

    def update_stats(self) -> None:
        s = self.session
        pct = s.percent(self.quiz)
        hints = "[green]ON[/]" if s.hints_enabled else "[dim]OFF[/]"
        self.query_one("#stats", Static).update(
            f"Answered [b]{s.answered_count}[/]/{len(self.quiz)}   "
            f"Correct [b]{s.correct_count(self.quiz)}[/]   "
            f"Score [b]{pct:.0f}%[/]   "
            f"Hints {hints}"
        )

    def _is_last(self) -> bool:
        return self.session.index >= len(self.quiz) - 1

    # ---- interaction -------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id and event.button.id.startswith("opt-"):
            self.action_select(int(event.button.id.split("-")[1]))

    def action_select(self, index: int) -> None:
        if self.answered or index >= len(self.current.options):
            return
        self.answered = True
        self.session.record(self.session.index, index)
        self.query_one("#hint", Static).display = False
        self._reveal(index)
        self.update_stats()
        self.session.save()

    async def action_next(self) -> None:
        if not self.answered:
            return
        if self._is_last():
            self.session.completed = True
            self.session.save()
            self.app.switch_screen(ResultsScreen(self.quiz, self.session))
            return
        self.session.index += 1
        self.session.save()
        await self.load_question()

    def action_toggle_hints(self) -> None:
        self.session.hints_enabled = not self.session.hints_enabled
        self.session.save()
        hint_widget = self.query_one("#hint", Static)
        if self.session.hints_enabled and not self.answered:
            hint_widget.update(f"[dim italic]💡 {self.current.hint}[/]")
            hint_widget.display = True
        else:
            hint_widget.display = False
        self.update_stats()

    def action_reset(self) -> None:
        async def _do(confirm: bool | None) -> None:
            if confirm:
                self.session.reset()
                await self.load_question()

        self.app.push_screen(
            ConfirmScreen("Reset all progress for this quiz?"), _do
        )

    def action_menu(self) -> None:
        self.session.save()
        self.app.show_menu()  # type: ignore[attr-defined]

    def action_quit(self) -> None:
        self.session.save()
        self.app.exit()


class ResultsScreen(Screen):
    """Final score summary."""

    BINDINGS = [
        Binding("r", "restart", "Restart"),
        Binding("m", "menu", "Menu"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, quiz: Quiz, session: Session) -> None:
        super().__init__()
        self.quiz = quiz
        self.session = session

    def compose(self) -> ComposeResult:
        yield Header()
        s = self.session
        pct = s.percent(self.quiz)
        correct = s.correct_count(self.quiz)
        grade = (
            "[b green]Great work![/]"
            if pct >= 80
            else "[b yellow]Keep practising.[/]"
            if pct >= 60
            else "[b red]More review needed.[/]"
        )
        with Center():
            with Vertical(id="results-card"):
                yield Label(f"[b]{self.quiz.title}[/]", id="results-title")
                yield Static(
                    f"\nScore: [b]{pct:.0f}%[/]\n"
                    f"Correct: [b]{correct}[/] / {s.answered_count} answered "
                    f"({len(self.quiz)} total)\n\n{grade}\n",
                    id="results-body",
                )
                yield Button("Restart quiz", variant="primary", id="restart")
                yield Button("Back to menu", id="menu")
                yield Button("Quit", variant="error", id="quit")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        getattr(self, f"action_{event.button.id}")()

    def action_restart(self) -> None:
        self.session.reset()
        self.app.switch_screen(QuizScreen(self.quiz, self.session))

    def action_menu(self) -> None:
        self.app.show_menu()  # type: ignore[attr-defined]

    def action_quit(self) -> None:
        self.app.exit()


class PrepApp(App):
    """Quiz practice TUI."""

    CSS_PATH = "app.tcss"
    TITLE = "cli-prep"

    def __init__(
        self, quizzes_dir: Path, quiz_path: Path | None = None
    ) -> None:
        super().__init__()
        self.quizzes_dir = Path(quizzes_dir)
        self._initial_quiz = quiz_path

    def on_mount(self) -> None:
        if self._initial_quiz is not None:
            screen = self._build_quiz(self._initial_quiz)
            if screen is not None:
                self.push_screen(screen)
                return
        self.push_screen(self._build_menu())

    def _build_menu(self) -> MenuScreen:
        return MenuScreen(discover_quizzes(self.quizzes_dir))

    def _build_quiz(self, path: Path) -> "QuizScreen | None":
        try:
            quiz = Quiz.load(path)
        except QuizError as exc:
            self.notify(str(exc), severity="error", timeout=8)
            return None
        return QuizScreen(quiz, Session.for_quiz(quiz))

    def show_menu(self) -> None:
        self.switch_screen(self._build_menu())

    def open_quiz(self, path: Path) -> None:
        screen = self._build_quiz(path)
        if screen is not None:
            self.switch_screen(screen)
