# AGENTS.md

Guidance for coding agents working in this repository.

## Project Snapshot

- Project name: `oobot`
- Language: Python (>=3.10)
- Packaging: `pyproject.toml` + hatchling
- Runtime model: Telegram bot that controls OpenCode sessions via tmux
- Main package path: `src/oobot`
- CLI entrypoint: `oobot` -> `oobot.main:main`

## Agent Priorities

1. Preserve topic-based architecture: 1 Telegram topic = 1 tmux window = 1 OpenCode session.
2. Keep behavior consistent with `OPENCODE.md` principles.
3. Avoid broad refactors unless explicitly requested.
4. Favor small, local, typed changes with clear logging.
5. Do not introduce truncation in transcript parsing logic.

## Environment and Setup

- This machine's Python toolchain policy:
  - Use `pyenv` to manage/select Python versions.
  - Use `uv` to manage the project virtualenv and dependency versions.
  - Do not install project dependencies with global `pip`.
- Always use the project-managed virtual environment through `uv`.
- Do not use global `python`/`pip`; avoid environment pollution.
- Runtime env vars are loaded from `.env` in the current project directory (cwd).
- If Python version changes, update via `pyenv` first, then re-sync deps with `uv sync`.
- Quick checks:
  - `pyenv version`
  - `uv run python -V`
- Create/update environment with:
  - `uv sync`
- Install dev tools (pyright) when needed:
  - `uv sync --extra dev`
- Run bot locally:
  - `uv run oobot`
- Run Python modules/commands via:
  - `uv run python ...`
  - `uv run <tool> ...`
- Install hook into OpenCode settings:
  - `uv run oobot hook --install`

## OpenCode Global Configuration

- OpenCode global settings file: `~/.config/opencode/opencode.json`.
- OOBot hook install writes a plugin bridge file at `~/.config/opencode/plugins/oobot-session-map.js`.
- OpenCode session data is read from: `~/.local/share/opencode/storage` (with legacy fallback to `~/.opencode/projects`).
- OOBot runtime state is separate and stored under: `./.oobot` by default (or `$OOBOT_DIR`).

## Build / Lint / Test Commands

This project currently has **no committed test suite** under `tests/`.

### Build / package checks

- Build wheel/sdist:
  - `uv build`
- Validate package metadata quickly:
  - `uv run python -m pip show oobot` (if installed)

### Type checking (primary quality gate)

- Required by project guidance after code changes:
  - `uv run pyright src/oobot`

### Lint / formatting

- No dedicated linter/formatter config (ruff/black/isort) is present.
- If you introduce one, keep it scoped and document it in README + this file.

### Tests

- Run all tests (when tests are added):
  - `uv run pytest`
- Run a single test file:
  - `uv run pytest tests/test_session.py`
- Run a single test function:
  - `uv run pytest tests/test_session.py::test_resolve_window_for_thread`
- Run tests by keyword:
  - `uv run pytest -k "history and pagination"`

If `pytest` is missing, add it as a dev dependency first.

## Useful Runtime / Ops Commands

- Restart service in tmux main window:
  - `./scripts/restart.sh`
- Inspect bot startup manually:
  - `uv run oobot`
- Trigger hook manually with JSON stdin (debug flow):
  - `echo '{...}' | uv run oobot hook`

## Repository-Specific Architecture Rules

Derived from `OPENCODE.md` and existing code:

1. Topic-only mode; no fallback for non-topic/general-thread routing.
2. State is window-centric (tmux window names are stable anchors).
3. Session tracking depends on plugin-bridged `session.created` events writing `session_map.json`.
4. Monitoring uses OpenCode storage backend (with legacy JSONL byte-offset fallback).
5. Tool use/result pairing relies on `tool_use_id`, including cross-poll carryover.
6. Telegram output uses MarkdownV2 conversion with plain-text fallback.
7. Sending layer handles splitting for Telegram limits; parser layer should keep full content.

## Code Style Guidelines

### Imports

- Use standard order:
  1) stdlib
  2) third-party
  3) local package imports
- Prefer explicit imports over wildcard imports.
- Avoid import-time side effects unless required (config singleton is intentional here).
- In modules with potential cycles, use deferred imports inside functions (pattern used in monitor loop).

### Formatting

- Follow existing PEP 8 style and line wrapping patterns.
- Keep functions focused and reasonably short.
- Keep log messages concise and contextual.
- Preserve existing docstring-first module structure.

### Typing

- Use modern Python typing (`X | None`, `dict[str, Any]`, dataclasses).
- Type all public functions and methods.
- Keep dataclass field types explicit.
- Avoid introducing untyped helper functions in core flows.

### Naming Conventions

- Modules/files: `snake_case.py`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Dataclasses/classes: `PascalCase`
- Callback constants in handlers: `CB_*` prefix (existing convention)

### Error Handling

- Prefer explicit, narrow exception handling (`json.JSONDecodeError`, `OSError`, etc.).
- Log actionable context on failure (session/window/file identifiers).
- Degrade gracefully for Telegram API failures (follow safe send/edit helpers).
- Avoid silent `except Exception` unless there is a strong reason; if used, log clearly.

### Async and Concurrency

- Keep blocking I/O off the event loop (`asyncio.to_thread`, `aiofiles`).
- Preserve per-user message queue ordering guarantees.
- Maintain rate-limiting protections to avoid Telegram flood control.
- Be careful when editing polling loops; avoid duplicate sends and state races.

### State and Persistence

- Use atomic JSON writes for state files.
- Keep in-memory and persisted mappings consistent:
  - `thread_bindings`
  - window/session associations
  - monitor offsets
- Handle file truncation scenarios explicitly (already implemented in monitor/session logic).

### Telegram UX Conventions

- Prefer inline keyboard flows for interaction.
- Use `answer_callback_query` for immediate callback feedback.
- Prefer editing existing status/UI messages where appropriate over sending duplicates.
- Preserve MarkdownV2 fallback behavior.

## Documentation Rules for Agents

- Every Python module should start with a meaningful module docstring.
- Update module docstrings when responsibilities materially change.
- Keep README/README_CN and code behavior aligned when changing commands/env vars.
- Keep naming consistent as `oobot` across docs, commands, and examples.

## CI / External Agent Rules

- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` files were found.
- GitHub workflows present:
  - `.github/workflows/claude.yml`
  - `.github/workflows/claude-code-review.yml`
- These workflows run Claude-based automation; they do not define local lint/test policy.

## Safety Checklist Before Submitting Changes

1. Run type check: `uv run pyright src/oobot`.
2. If tests exist for your area, run targeted pytest first, then full suite.
3. Verify no regressions in topic binding/session mapping flows.
4. Verify Telegram formatting still works (MarkdownV2 + fallback paths).
5. Keep changes minimal and architecture-consistent.
