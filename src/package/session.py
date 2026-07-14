"""Persistence of quiz progress so sessions can be resumed or reset."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .models import Quiz

SESSIONS_DIR = Path.home() / ".cli-prep" / "sessions"


def _slug(quiz_path: Path) -> str:
    resolved = str(Path(quiz_path).expanduser().resolve())
    digest = hashlib.md5(resolved.encode("utf-8")).hexdigest()[:8]
    return f"{Path(quiz_path).stem}-{digest}"


def session_file(quiz_path: Path) -> Path:
    return SESSIONS_DIR / f"{_slug(quiz_path)}.json"


@dataclass
class Session:
    """Mutable progress for one quiz: current position and chosen answers."""

    quiz_path: Path
    quiz_title: str
    num_questions: int
    index: int = 0
    # question index (as str for JSON keys) -> selected option index
    answers: dict[int, int] = field(default_factory=dict)
    hints_enabled: bool = False
    completed: bool = False

    # ---- persistence -------------------------------------------------

    @classmethod
    def for_quiz(cls, quiz: Quiz) -> "Session":
        """Load an existing session for ``quiz`` or start a fresh one."""
        existing = cls.load(quiz.path)
        if existing is not None and existing.num_questions == len(quiz):
            return existing
        return cls(
            quiz_path=quiz.path,
            quiz_title=quiz.title,
            num_questions=len(quiz),
        )

    @classmethod
    def load(cls, quiz_path: Path) -> "Session | None":
        path = session_file(quiz_path)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return cls(
            quiz_path=Path(data["quiz_path"]),
            quiz_title=data.get("quiz_title", ""),
            num_questions=data.get("num_questions", 0),
            index=data.get("index", 0),
            answers={int(k): int(v) for k, v in data.get("answers", {}).items()},
            hints_enabled=data.get("hints_enabled", False),
            completed=data.get("completed", False),
        )

    def save(self) -> None:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "quiz_path": str(self.quiz_path),
            "quiz_title": self.quiz_title,
            "num_questions": self.num_questions,
            "index": self.index,
            "answers": {str(k): v for k, v in self.answers.items()},
            "hints_enabled": self.hints_enabled,
            "completed": self.completed,
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        session_file(self.quiz_path).write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def delete(self) -> None:
        """Remove the saved session file, if any."""
        session_file(self.quiz_path).unlink(missing_ok=True)

    def reset(self) -> None:
        """Clear all progress (in memory and on disk)."""
        self.index = 0
        self.answers.clear()
        self.completed = False
        self.delete()

    # ---- scoring -----------------------------------------------------

    def record(self, question_index: int, choice: int) -> None:
        self.answers[question_index] = choice

    @property
    def answered_count(self) -> int:
        return len(self.answers)

    def correct_count(self, quiz: Quiz) -> int:
        return sum(
            1
            for qi, choice in self.answers.items()
            if 0 <= qi < len(quiz) and quiz.questions[qi].is_correct(choice)
        )

    def percent(self, quiz: Quiz) -> float:
        answered = self.answered_count
        if answered == 0:
            return 0.0
        return 100.0 * self.correct_count(quiz) / answered

    @property
    def has_progress(self) -> bool:
        return bool(self.answers) or self.index > 0
