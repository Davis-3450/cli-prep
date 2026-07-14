"""Quiz data model and loader for the JSON files in ``quizzes/``."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_QUESTION_FIELDS = ("question", "options", "answer", "explanation", "hint")


@dataclass(frozen=True)
class Question:
    """A single multiple-choice question."""

    question: str
    options: list[str]
    answer: str
    explanation: str
    hint: str

    @property
    def answer_index(self) -> int:
        """Index of the correct option, or ``-1`` if it cannot be matched."""
        if self.answer in self.options:
            return self.options.index(self.answer)
        target = self.answer.strip()
        for i, option in enumerate(self.options):
            if option.strip() == target:
                return i
        return -1

    def is_correct(self, choice: int) -> bool:
        return choice == self.answer_index


@dataclass
class Quiz:
    """A quiz: metadata plus a list of questions, loaded from a JSON file."""

    title: str
    description: str
    questions: list[Question]
    path: Path

    def __len__(self) -> int:
        return len(self.questions)

    @classmethod
    def load(cls, path: str | Path) -> "Quiz":
        path = Path(path).expanduser().resolve()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise QuizError(f"Quiz file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise QuizError(f"Invalid JSON in {path}: {exc}") from exc

        raw_questions = data.get("questions")
        if not isinstance(raw_questions, list) or not raw_questions:
            raise QuizError(f"{path} has no questions.")

        questions: list[Question] = []
        for i, q in enumerate(raw_questions):
            missing = [f for f in _QUESTION_FIELDS if f not in q]
            if missing:
                raise QuizError(f"Question {i} in {path} is missing: {missing}")
            if not isinstance(q["options"], list) or len(q["options"]) < 2:
                raise QuizError(f"Question {i} in {path} needs at least 2 options.")
            questions.append(Question(**{f: q[f] for f in _QUESTION_FIELDS}))

        return cls(
            title=data.get("title", path.stem),
            description=data.get("description", ""),
            questions=questions,
            path=path,
        )


class QuizError(Exception):
    """Raised when a quiz file cannot be loaded or is malformed."""


def discover_quizzes(directory: str | Path) -> list[Path]:
    """Return the JSON quiz files in ``directory`` (excluding schema files)."""
    directory = Path(directory).expanduser()
    if not directory.is_dir():
        return []
    return sorted(
        p
        for p in directory.glob("*.json")
        if p.name not in {"schema.json"} and not p.name.endswith(".schema.json")
    )
