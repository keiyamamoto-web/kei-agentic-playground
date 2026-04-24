# Skill: Gemini CLI

## Purpose

Allows the agent to use the `gemini` CLI tool for advanced AI-driven tasks, managing MCP servers, and leveraging Gemini's own development capabilities.

## Guidelines

- **Always use non-interactive mode**: When executing `gemini` via `run_command`, use the `-p` or `--prompt` flag to avoid hanging the terminal.
- **Capture Output**: Use `-o json` or `-o text` if specific formatting is needed for parsing.
- **Approval Mode**: For automated tasks, consider `--approval-mode yolo` if safe, but default to standard execution.

## Example Commands

### 1. Run a one-off query

```bash
gemini --prompt "Analyze the security of this project"
```

### 2. List MCP servers

```bash
gemini mcp list
```

### 3. Check CLI version and status

```bash
gemini --version
```

## Reference

See [.agents/gemini_cli_reference.md](../gemini_cli_reference.md) for full documentation.
