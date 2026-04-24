# Gemini CLI Reference

## Overview

Gemini CLI is a terminal-based interface for Gemini, optimized for software engineering tasks and development workflows. It supports interactive chat, non-interactive (headless) execution, MCP servers, and IDE integration.

## Usage

```bash
gemini [options] [command]
```

### Key Subcommands

- `gemini mcp`: Manage MCP servers.
- `gemini extensions`: Manage Gemini CLI extensions.
- `gemini skills`: Manage agent skills.
- `gemini hooks`: Manage hooks.
- `gemini [query]`: Launch in interactive mode (default).

### Options

- `-p, --prompt <text>`: Run in **non-interactive (headless)** mode. (Recommended for AI agents).
- `-m, --model <model>`: Specify the model to use.
- `-y, --yolo`: Automatically accept all actions (YOLO mode).
- `-r, --resume <session>`: Resume a previous session.
- `-o, --output-format <format>`: Set output format (`text`, `json`, `stream-json`).

---

## IDE Integration (IDE Mode)

Gemini CLI can connect to your IDE (like VS Code) to provide workspace context and native features.

### Slash Commands (Inside Gemini)

- `/ide install`: Manually trigger companion extension installation.
- `/ide enable`: Enable the connection between CLI and IDE.
- `/ide disable`: Disable the connection.

### Features

- **Workspace Context**: Automatically gains awareness of open files, cursor position, and selected text.
- **Native Diffing**: Suggested code changes open in the IDE's native diff viewer.

### Accepting Diffs

- Click the checkmark in the diff editor.
- Save the file (`Cmd+S` / `Ctrl+S`).
- Use VS Code Command Palette: `Gemini CLI: Accept Diff`.

---

## Authentication

Gemini CLI uses its own authentication state, separate from `gcloud`.

- **Location**: Credentials are stored in `~/.config/gcloud/application_default_credentials.json` (if using ADC) or tool-specific files in `~/.gemini/`.
- **Resetting Auth**: If stuck in a permission loop, delete `~/.gemini/oauth_creds.json` and `~/.gemini/google_accounts.json` to force a re-login.

---

## Slash Commands (Interactive Mode)

- `/quit` or `/exit`: Exit the session.
- `/clear`: Clear the session history.
- `/model`: View/change model settings.
- `/ide`: Manage IDE integration.
- `/help`: Show available slash commands.
