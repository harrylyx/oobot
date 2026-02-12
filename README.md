# OOBot

[中文文档](README_CN.md)

OOBot is a Telegram bot for controlling OpenCode sessions running in tmux.

> This project is adapted from [ccbot](https://github.com/six-ddc/ccbot) and has been refocused for OpenCode.

## What It Is

OOBot is built around one strict model:

- 1 Telegram topic = 1 tmux window = 1 OpenCode session

The bot does not create a second OpenCode API session. It controls the same terminal process you can attach to locally with tmux.

## Current Feature Set

- Topic-based session routing (topic-only mode)
- Message forwarding from Telegram text to OpenCode via tmux keystrokes
- Real-time OpenCode output monitoring from storage transcripts
- Interactive prompt handling (AskUserQuestion / ExitPlanMode)
- History pagination with newest page first (`/history`)
- Terminal screenshot capture with control key buttons (`/screenshot`)
- Mobile shortcut panel (`/keys`) for common commands and keys
- File upload (Telegram document -> project directory)
- File download (`/download relative/path`)
- Lightweight file utilities (`/pwd`, `/ls`)
- Session tracking through OpenCode plugin bridge (`session_map.json`)

## Requirements

- Python 3.10+
- `uv`
- `tmux`
- `opencode` CLI
- A Telegram bot in a supergroup with Topics enabled

## Install

```bash
uv sync
```

Optional (for local type checking):

```bash
uv sync --extra dev
```

## Configuration

Copy environment template:

```bash
cp .env.example .env
```

`oobot` reads `.env` from the current working directory where you run `uv run oobot`.

Required variables:

| Variable | Description |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Token from BotFather |
| `ALLOWED_USERS` | Comma-separated Telegram user IDs |

Optional variables:

| Variable | Default | Description |
| --- | --- | --- |
| `OOBOT_DIR` | `./.oobot` | Runtime state directory |
| `TMUX_SESSION_NAME` | `oobot` | tmux session name |
| `OPENCODE_COMMAND` | `opencode` | Command started in new windows |
| `OPENCODE_STORAGE_PATH` | `~/.local/share/opencode/storage` | OpenCode storage backend |
| `OPENCODE_PROJECTS_PATH` | `~/.opencode/projects` | Legacy JSONL backend |
| `MONITOR_POLL_INTERVAL` | `2.0` | Monitor polling interval in seconds |
| `TELEGRAM_TRUST_ENV` | `false` | Trust env/system proxy settings for Telegram requests |
| `TELEGRAM_PROXY` | unset | Explicit proxy URL for Telegram requests |

By default, OOBot uses a direct Telegram connection (`TELEGRAM_TRUST_ENV=false`), which avoids accidental macOS/system proxy auto-detection.

## Hook Installation (Recommended)

Install the OpenCode plugin bridge:

```bash
uv run oobot hook --install
```

This writes:

- `~/.config/opencode/plugins/oobot-session-map.js`

The bridge updates `$OOBOT_DIR/session_map.json`, which OOBot uses to map tmux windows to active OpenCode sessions.

## Run

```bash
uv run oobot
```

## Topic Workflow

1. Create a new Telegram topic.
2. Send any text message in that topic.
3. OOBot opens a directory browser.
4. Confirm a directory.
5. OOBot creates a tmux window, starts OpenCode, binds that topic, and forwards your pending message.

To end a session, close the topic. OOBot will kill the associated tmux window and clean up bindings.

## Commands

Bot-side commands:

| Command | Description |
| --- | --- |
| `/start` | Show welcome text |
| `/history` | Show history for current topic |
| `/screenshot` | Capture pane screenshot with key controls |
| `/keys` | Show mobile shortcut panel |
| `/esc` | Send Escape |
| `/pwd` | Show current project directory |
| `/ls [path]` | List files/dirs under current project |
| `/download <path>` | Download file from current project |

OpenCode command forwarding:

- Menu shortcuts: `/clear`, `/compact`, `/cost`, `/help`, `/memory`, `/session`
- Any unknown `/command` is also forwarded to OpenCode as-is

## File Transfer Behavior

Upload:

- Send a Telegram document in a bound topic.
- Optional caption can set destination path:
  - `src/data/input.json`
  - `/upload src/data/input.json`
- Destination is restricted to the current project directory.
- Name conflicts are auto-resolved with numeric suffixes.

Download:

- Use `/download relative/path/to/file`.
- Path is restricted to the current project directory.

Limits:

- Max transfer size is currently 20 MB.

## Runtime State

| Path | Purpose |
| --- | --- |
| `$OOBOT_DIR/state.json` | Topic bindings and user offsets |
| `$OOBOT_DIR/session_map.json` | Window -> OpenCode session mapping |
| `$OOBOT_DIR/monitor_state.json` | Monitor offsets and polling state |

## Development Notes

- Primary quality gate:

```bash
uv run pyright src/oobot
```

- Restart helper:

```bash
./scripts/restart.sh
```
