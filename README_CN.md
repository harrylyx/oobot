# OOBot

OOBot 是一个用于通过 Telegram 控制 tmux 中 OpenCode 会话的机器人。

> 本项目基于 [ccbot](https://github.com/six-ddc/ccbot) 修改，并围绕 OpenCode 场景持续演进。

## 项目定位

OOBot 采用严格的一一映射模型：

- 1 个 Telegram 话题 = 1 个 tmux 窗口 = 1 个 OpenCode 会话

它不是再创建一套独立 API 会话，而是直接操作你本机 tmux 里的同一个 OpenCode 进程。

## 当前功能

- 话题绑定路由（仅话题模式）
- 文本消息通过 tmux 按键转发到 OpenCode
- 从 OpenCode 存储记录实时监控并推送结果
- 交互式问题处理（AskUserQuestion / ExitPlanMode）
- 历史消息分页（`/history` 默认最新页）
- 终端截图和按键控制（`/screenshot`）
- 移动端快捷面板（`/keys`）
- 文件上传（Telegram 文档 -> 项目目录）
- 文件下载（`/download 相对路径`）
- 轻量文件操作（`/pwd`、`/ls`）
- 通过插件桥接维护会话映射（`session_map.json`）

## 运行依赖

- Python 3.10+
- `uv`
- `tmux`
- `opencode` 命令行
- 已开启话题模式的 Telegram 群组机器人

## 安装

```bash
uv sync
```

如需本地类型检查工具：

```bash
uv sync --extra dev
```

## 配置

复制环境变量模板：

```bash
cp .env.example .env
```

`oobot` 会读取你当前执行 `uv run oobot` 目录下的 `.env`。

必填项：

| 变量 | 说明 |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | BotFather 提供的机器人 Token |
| `ALLOWED_USERS` | 允许访问的 Telegram 用户 ID，逗号分隔 |

可选项：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `OOBOT_DIR` | `./.oobot` | 运行时状态目录 |
| `TMUX_SESSION_NAME` | `oobot` | tmux 会话名 |
| `OPENCODE_COMMAND` | `opencode` | 新窗口中启动命令 |
| `OPENCODE_STORAGE_PATH` | `~/.local/share/opencode/storage` | OpenCode 存储后端路径 |
| `OPENCODE_PROJECTS_PATH` | `~/.opencode/projects` | 旧版 JSONL 路径 |
| `MONITOR_POLL_INTERVAL` | `2.0` | 轮询间隔（秒） |

## 安装 Hook（推荐）

安装 OpenCode 插件桥接：

```bash
uv run oobot hook --install
```

会写入：

- `~/.config/opencode/plugins/oobot-session-map.js`

该桥接会更新 `$OOBOT_DIR/session_map.json`，用于维护 tmux 窗口与 OpenCode 会话的映射。

## 启动

```bash
uv run oobot
```

## 话题工作流

1. 在 Telegram 新建一个话题。
2. 在该话题发送任意文本。
3. OOBot 弹出目录浏览器。
4. 选择并确认目录。
5. OOBot 创建 tmux 窗口、启动 OpenCode、绑定话题并转发刚才消息。

结束会话时，直接关闭该话题。OOBot 会自动终止对应 tmux 窗口并清理绑定。

## 命令

Bot 本地命令：

| 命令 | 说明 |
| --- | --- |
| `/start` | 欢迎信息 |
| `/history` | 查看当前话题历史消息 |
| `/screenshot` | 终端截图（含按键控制） |
| `/keys` | 打开移动端快捷面板 |
| `/esc` | 发送 Escape |
| `/pwd` | 查看当前项目目录 |
| `/ls [path]` | 列出当前项目下文件/目录 |
| `/download <path>` | 下载当前项目中的文件 |

OpenCode 命令转发：

- 菜单快捷：`/clear`、`/compact`、`/cost`、`/help`、`/memory`
- 其他未知 `/command` 也会原样转发到 OpenCode

## 文件传输行为

上传：

- 在已绑定话题中发送 Telegram 文档。
- 可用 caption 指定目标路径：
  - `src/data/input.json`
  - `/upload src/data/input.json`
- 目标路径必须位于当前项目目录内。
- 同名文件会自动添加数字后缀避免覆盖。

下载：

- 使用 `/download 相对路径/文件名`。
- 路径限制在当前项目目录内。

限制：

- 当前最大传输大小为 20 MB。

## 运行状态文件

| 路径 | 用途 |
| --- | --- |
| `$OOBOT_DIR/state.json` | 话题绑定与用户读取偏移 |
| `$OOBOT_DIR/session_map.json` | 窗口 -> OpenCode 会话映射 |
| `$OOBOT_DIR/monitor_state.json` | 监控偏移与轮询状态 |

## 开发说明

- 主要质量检查：

```bash
uv run pyright src/oobot
```

- 重启辅助脚本：

```bash
./scripts/restart.sh
```
