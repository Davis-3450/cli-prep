# cli-prep

A terminal UI (TUI) for practising multiple-choice quizzes — built with
[Textual](https://textual.textualize.io/) and [Typer](https://typer.tiangolo.com/).

Study from JSON question banks, pick answers, get instant feedback with
explanations, toggle hints on/off, track your running score, and **resume or
reset** a session at any time.

## Features

- 🎯 **Choose answers** with the mouse or number keys (`1`–`5`)
- 💡 **Hints** you can toggle on/off (`h`)
- 📊 **Live score** — answered count, correct count, and percentage
- 💾 **Resume** — progress is saved automatically; reopen a quiz to continue
- 🔄 **Reset** a quiz's progress (`r` in the TUI, or `prep reset <file>`)
- 🧾 **Explanations** shown after each answer
- 📚 Multiple quizzes discovered from a `quizzes/` folder

## Install

```bash
uv sync            # set up the environment
uv run prep        # launch the TUI (menu)
```

Or install it as a tool:

```bash
uv tool install .
prep
```

## Usage

```bash
prep                       # open the quiz menu
prep start                 # same as above
prep start quizzes/security-plus.json   # jump straight into a quiz
prep list                  # list quizzes and saved progress
prep reset quizzes/security-plus.json   # clear saved progress for a quiz
prep start -d ./my-quizzes # use a different quizzes directory
```

### Keys (in the quiz)

| Key       | Action                          |
|-----------|---------------------------------|
| `1`–`5`   | Select an answer                |
| `space` / `n` | Next question (after answering) |
| `h`       | Toggle hints                    |
| `r`       | Reset this quiz's progress      |
| `m`       | Back to the quiz menu           |
| `q`       | Save and quit                   |

Progress is stored per-quiz under `~/.cli-prep/sessions/`.

## Quiz format

Quizzes are JSON files in `quizzes/` (see `quizzes/schema.json`):

```json
{
  "title": "Geography Quiz",
  "description": "Test your knowledge of world geography.",
  "questions": [
    {
      "question": "Q: What is the capital of France?",
      "options": ["A: Paris", "B: London", "C: Berlin", "D: Madrid"],
      "answer": "A: Paris",
      "explanation": "The capital of France is Paris.",
      "hint": "It's also called the 'City of Light'."
    }
  ]
}
```

`answer` must match one of the `options` exactly.

## Development

```bash
uv sync --group dev
uv run pytest        # models, sessions, and TUI (Pilot) tests
uv run ruff check src tests
```

## Project layout

```
src/package/
  models.py    # Quiz / Question loading + grading
  session.py   # save / load / reset / resume progress
  tui.py       # Textual app: menu, quiz, results screens
  app.tcss     # TUI styles
  main.py      # Typer CLI entry point (`prep`)
quizzes/       # JSON question banks
tests/         # pytest suite (headless TUI via Pilot)
```
