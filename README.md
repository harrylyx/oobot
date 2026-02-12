# OOBot

[中文文档](README_CN.md)

Control OpenCode sessions remotely via Telegram — monitor, interact, and manage AI coding sessions running in tmux.

> This project is adapted from [ccbot](https://github.com/six-ddc/ccbot) and further evolved for OpenCode workflows.

https://github.com/user-attachments/assets/15ffb38e-5eb9-4720-93b9-412e4961dc93

## Why OOBot?

OpenCode runs in your terminal. When you step away from your computer — commuting, on the couch, or just away from your desk — the session keeps working, but you lose visibility and control.

OOBot solves this by letting you **seamlessly continue the same session from Telegram**. The key insight is that it operates on **tmux**, not the OpenCode SDK. Your OpenCode process stays exactly where it is, in a tmux window on your machine. OOBot simply reads its output and sends keystrokes to it. This means:

- **Switch from desktop to phone mid-conversation** — OpenCode is working on a refactor? Walk away, keep monitoring and responding from Telegram.
- **Switch back to desktop anytime** — Since the tmux session was never interrupted, just `tmux attach` and you're back in the terminal with full scrollback and context.
- **Run multiple sessions in parallel** — Each Telegram topic maps to a separate tmux window, so you can juggle multiple projects from one chat group.

Other Telegram bots for OpenCode typically wrap the OpenCode SDK to create separate API sessions. Those sessions are isolated — you can't resume them in your terminal. OOBot takes a different approach: it's just a thin control layer over tmux, so the terminal remains the source of truth and you never lose the ability to switch back.

In fact, OOBot itself was built this way — iterating on itself through OpenCode sessions monitored and driven from Telegram via OOBot.

## Features

- **Topic-based sessions** — Each Telegram topic maps 1:1 to a tmux window and OpenCode session
- **Real-time notifications** — Get Telegram messages for assistant responses, thinking content, tool use/result, and local command output
- **Interactive UI** — Navigate AskUserQuestion, ExitPlanMode, and Permission Prompts via inline keyboard
- **Send messages** — Forward text to OpenCode via tmux keystrokes
- **File transfer** — Upload Telegram documents into the bound project, and download files with `/download`
- **Slash command forwarding** — Send any `/command` directly to OpenCode (e.g. `/clear`, `/compact`, `/cost`)
- **Mobile shortcuts** — Open a shortcut panel (`/keys`) for one-tap OpenCode commands and control keys
- **Create new sessions** — Start OpenCode sessions from Telegram via directory browser
- **Kill sessions** — Close a topic to auto-kill the associated tmux window
- **Message history** — Browse conversation history with pagination (newest first)
- **Plugin-based session tracking** — Auto-associates tmux windows with OpenCode sessions via `session.created` bridge
- **Persistent state** — Thread bindings and read offsets survive restarts

## Installation

```bash
cd oobot
uv sync
```

Use the project virtual environment via `uv` commands (`uv run ...`). Avoid global `python`/`pip` installs.
On this machine, manage Python versions with `pyenv`, then use `uv` for environment/package sync (for example: `pyenv version`, then `uv sync`).

## Configuration

**1. Create a Telegram bot and enable Threaded Mode:**

1. Chat with [@BotFather](https://t.me/BotFather) to create a new bot and get your bot token
2. Open @BotFather's profile page, tap **Open App** to launch the mini app
3. Select your bot, then go to **Settings** > **Bot Settings**
4. Enable **Threaded Mode**

**2. Configure environment variables:**

```bash
cp .env.example .env
```

`oobot` reads `.env` from the current project directory (where you run the command).

**Required:**

| Variable             | Description                       |
| -------------------- | --------------------------------- |
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather         |
| `ALLOWED_USERS`      | Comma-separated Telegram user IDs |

**Optional:**

| Variable                | Default    | Description                                      |
| ----------------------- | ---------- | ------------------------------------------------ |
| `OOBOT_DIR`             | `./.oobot` | Config/state directory |
| `TMUX_SESSION_NAME`     | `oobot`    | Tmux session name                                |
| `OPENCODE_COMMAND`      | `opencode` | Command to run in new windows                    |
| `OPENCODE_STORAGE_PATH` | `~/.local/share/opencode/storage` | OpenCode storage backend path |
| `OPENCODE_PROJECTS_PATH` | `~/.opencode/projects` | Legacy OpenCode JSONL path |
| `MONITOR_POLL_INTERVAL` | `2.0`      | Polling interval in seconds                      |

> If running on a VPS where there's no interactive terminal to approve permissions, consider:
>
> ```
> OPENCODE_COMMAND=IS_SANDBOX=1 opencode --dangerously-skip-permissions
> ```

## Hook Setup (Recommended)

Auto-install via CLI:

```bash
uv run oobot hook --install
```

This installs a plugin bridge at `~/.config/opencode/plugins/oobot-session-map.js`.
OpenCode's current config schema does not accept a top-level `hooks` key.

This writes window-session mappings to `$OOBOT_DIR/session_map.json` (`./.oobot/` by default), so the bot automatically tracks which OpenCode session is running in each tmux window — even after `/clear` or session restarts.

## Usage

```bash
uv run oobot
```

### Commands

**Bot commands:**

| Command       | Description                     |
| ------------- | ------------------------------- |
| `/start`      | Show welcome message            |
| `/history`    | Message history for this topic  |
| `/screenshot` | Capture terminal screenshot     |
| `/keys`       | Show mobile shortcut keyboard   |
| `/esc`        | Send Escape to interrupt OpenCode |
| `/pwd`        | Show current project directory  |
| `/ls`         | List files in current project   |
| `/download`   | Download file from project      |

**OpenCode commands (forwarded via tmux):**

| Command    | Description                  |
| ---------- | ---------------------------- |
| `/clear`   | Clear conversation history   |
| `/compact` | Compact conversation context |
| `/cost`    | Show token/cost usage        |
| `/help`    | Show OpenCode help           |
| `/memory`  | Edit memory file             |

Any unrecognized `/command` is also forwarded to OpenCode as-is (e.g. `/review`, `/doctor`, `/init`).

### File Upload / Download

- Upload: send a Telegram **document** in a bound topic; OOBot saves it to the current project directory.
- Optional upload target: add a caption like `src/data/input.json` (or `/upload src/data/input.json`) to control the destination path.
- Download: run `/download relative/path/to/file` in the topic.

### Topic Workflow

**1 Topic = 1 Window = 1 Session.** The bot runs in Telegram Forum (topics) mode.

**Creating a new session:**

1. Create a new topic in the Telegram group
2. Send any message in the topic
3. A directory browser appears — select the project directory
4. A tmux window is created, `opencode` starts, and your pending message is forwarded

**Sending messages:**

Once a topic is bound to a session, just send text in that topic — it gets forwarded to OpenCode via tmux keystrokes.

**Killing a session:**

Close (or delete) the topic in Telegram. The associated tmux window is automatically killed and the binding is removed.

### Message History

Navigate with inline buttons:

```
📋 [project-name] Messages (42 total)

───── 14:32 ─────

👤 fix the login bug

───── 14:33 ─────

I'll look into the login bug...

[◀ Older]    [2/9]    [Newer ▶]
```

### Notifications

The monitor polls session JSONL files every 2 seconds and sends notifications for:

- **Assistant responses** — OpenCode's text replies
- **Thinking content** — Shown as expandable blockquotes
- **Tool use/result** — Summarized with stats (e.g. "Read 42 lines", "Found 5 matches")
- **Local command output** — stdout from commands like `git status`, prefixed with `❯ command_name`

Notifications are delivered to the topic bound to the session's window.

## Running OpenCode in tmux

### Option 1: Create via Telegram (Recommended)

1. Create a new topic in the Telegram group
2. Send any message
3. Select the project directory from the browser

### Option 2: Create Manually

```bash
tmux attach -t oobot
tmux new-window -n myproject -c ~/Code/myproject
# Then start OpenCode in the new window
opencode
```

The window must be in the `oobot` tmux session (configurable via `TMUX_SESSION_NAME`). The hook will automatically register it in `session_map.json` when OpenCode starts.

## Data Storage

| Path                            | Description                                                             |
| ------------------------------- | ----------------------------------------------------------------------- |
| `$OOBOT_DIR/state.json`         | Thread bindings, window states, and per-user read offsets               |
| `$OOBOT_DIR/session_map.json`   | Hook-generated `{tmux_session:window_name: {session_id, cwd}}` mappings |
| `$OOBOT_DIR/monitor_state.json` | Monitor byte offsets per session (prevents duplicate notifications)     |
| `~/.local/share/opencode/storage/` | OpenCode session data (read-only, current format)                    |
| `~/.opencode/projects/`         | OpenCode session data (legacy JSONL format, read-only)                  |

## File Structure

```
src/oobot/
├── __init__.py            # Package entry point
├── main.py                # CLI dispatcher (hook subcommand + bot bootstrap)
├── hook.py                # Hook subcommand for session tracking (+ --install)
├── config.py              # Configuration from environment variables
├── bot.py                 # Telegram bot setup, command handlers, topic routing
├── session.py             # Session management, state persistence, message history
├── session_monitor.py     # JSONL file monitoring (polling + change detection)
├── monitor_state.py       # Monitor state persistence (byte offsets)
├── transcript_parser.py   # OpenCode JSONL transcript parsing
├── terminal_parser.py     # Terminal pane parsing (interactive UI + status line)
├── markdown_v2.py         # Markdown → Telegram MarkdownV2 conversion
├── telegram_sender.py     # Message splitting + synchronous HTTP send
├── screenshot.py          # Terminal text → PNG image with ANSI color support
├── utils.py               # Shared utilities (atomic JSON writes, JSONL helpers)
├── tmux_manager.py        # Tmux window management (list, create, send keys, kill)
├── fonts/                 # Bundled fonts for screenshot rendering
└── handlers/
    ├── __init__.py        # Handler module exports
    ├── callback_data.py   # Callback data constants (CB_* prefixes)
    ├── directory_browser.py # Directory browser inline keyboard UI
    ├── history.py         # Message history pagination
    ├── interactive_ui.py  # Interactive UI handling (AskUser, ExitPlan, Permissions)
    ├── message_queue.py   # Per-user message queue + worker (merge, rate limit)
    ├── message_sender.py  # safe_reply / safe_edit / safe_send helpers
    ├── response_builder.py # Response message building (format tool_use, thinking, etc.)
    └── status_polling.py  # Terminal status line polling
```
