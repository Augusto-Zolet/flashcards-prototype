# Flashcard CLI Prototype – Technical Development Plan

> **Stack** Python 3.11 · Pydantic v2 · Rich (TTY UI) · Typer (CLI) · pytest · ruff/black · poetry (env + packaging)

---

## 1 Project Architecture

```
flashcards/
├── flashcards/              # application package (top‑level)
│   ├── __init__.py
│   ├── cli.py               # Typer entry‑point & main menu
│   ├── models/              # Pydantic entities
│   │   ├── __init__.py      # re‑exports models
│   │   ├── target.py
│   │   ├── example.py
│   │   ├── card.py
│   │   └── common.py
│   ├── services/            # domain logic
│   │   ├── __init__.py
│   │   ├── storage.py       # JSON read / write
│   │   ├── llm.py           # OpenAI wrapper (retries, rate‑limit)
│   │   ├── importer.py      # TSV import + LLM cleaning
│   │   ├── generator.py     # contextual example generator
│   │   └── scheduler.py     # SM‑2, queue builder
│   ├── ui/                  # Rich views
│   │   ├── __init__.py
│   │   ├── menu.py
│   │   └── cards.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── text.py          # normalise, distance helpers
│   ├── prompts/             # static LLM prompt templates (json/txt)
│   │   ├── __init__.py
│   │   └── contextual.json  # default prompt
├── tests/
│   ├── test_models.py
│   ├── test_scheduler.py
│   ├── test_importer.py
│   └── test_cli.py
├── data/                    # default data.json (git‑ignored)
├── README.md
├── pyproject.toml
└── CHANGELOG.md
```

### Key modules

| File                      | Responsibility                                                                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **models/**               | `target.py`, `example.py`, `card.py`, and `common.py`; each holds a single `BaseModel` and helpers, re‑exported in `models.__init__`. |
| **services/llm.py**       | Thin wrapper around OpenAI API; retries, rate‑limit, env‑key handling.                                                                |
| **services/importer.py**  | TSV → Example (original); uses `llm` wrapper for translation refinement; persists to storage.                                         |
| **services/generator.py** | Calls LLM for contextual examples; appends to storage; creates cards.                                                                 |
| **services/scheduler.py** | Builds session queue, applies unlock & requeue (+2) logic; updates SM‑2 stats.                                                        |
| **ui/menu.py**            | Main menu loop (Rich panels).                                                                                                         |
| **ui/cards.py**           | Draws Meaning, Word, Typing cards + feedback banners & hint stack.                                                                    |
| **prompts/**              | Reusable prompt templates consumed by `services.llm`.                                                                                 |

---

## 2 Development & Testing Cycles

| Iteration | Goal / Deliverable                                                                                          | Tests to add                                 |
| --------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| **0**     | Repo bootstrap, poetry, CI pipeline, **models, services, prompts packages**, storage I/O (read/write JSON). | `test_models`, `test_storage_roundtrip`.     |
| **1**     | Implement `services/llm.py` wrapper (mock); build `importer` to use it, confirm Example schema compliance.  | `test_importer_validates`, fixture TSV.      |
| **2**     | Build `generator` with mock LLM; generate contextual examples + auto‑cards.                                 | `test_generator_count`, `test_card_linkage`. |
| **3**     | Implement `scheduler` (queue order, unlock ladder, requeue +2).                                             | `test_scheduler_order`, `test_requeue_rule`. |
| **4**     | Render CLI menu & MeaningMCQ card (Rich); capture input, update stats.                                      | `test_cli_menu`, manual smoke run.           |
| **5**     | Add WordMCQ & Typing UIs, hint handling, prefix/suffix toggle.                                              | `test_hint_cycle`, `test_typing_eval`.       |
| **6**     | Integrate live OpenAI calls behind `--generate` flag, rate‑limit & API‑key env var.                         | e2e integration test with mocks.             |
| **7**     | Polish: error handling, config file, README usage guide.                                                    | full coverage pass + `ruff --fix`.           |

---

### README Snippet

```
poetry install
flashcards import my_words.tsv
flashcards
```

