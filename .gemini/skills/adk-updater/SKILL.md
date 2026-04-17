---
name: adk-updater
description: Check ADK Python release notes, update the google-adk package, and sync best practices to the adk-agent-builder skill.
---

# ADK Updater

This skill automates the process of checking for new releases of the `google-adk` package, updating the local installation, and syncing any new personal know-how or best practices to the `adk-agent-builder` skill.

## Workflow

When the user asks to "update ADK" or "check for ADK updates", follow these exact steps:

### 1. Fetch Release Notes

Use the `web_fetch` tool to read the latest release notes from the official ADK Python repository:
URL: `https://github.com/google/adk-python/releases`

Analyze the recent releases (especially the latest one) to identify:
- Version number
- New features or breaking changes
- Any changes to API usage, initialization, or deployment that affect how ADK agents are built.

### 2. Check Local Version

Use the `run_shell_command` tool to check the currently installed version of `google-adk`:
```bash
pip show google-adk
```

### 3. Update ADK Package

If the latest version from the release notes is newer than the installed version, or if the user explicitly requested an update, use the `run_shell_command` tool to update the package:
```bash
pip install -U google-adk
```
Inform the user about the successful update and summarize the key changes from the release notes.

### 4. Update the Agent Builder Skill

If the release notes indicate changes to how agents should be written (e.g., new `Tool` initialization patterns, changes to `GenerateContentConfig`, new features in `agent_engine`), you MUST update the `adk-agent-builder` skill to reflect these changes.

The `adk-agent-builder` skill is located at:
`C:\Users\219924\Desktop\So_workspace\.gemini\skills\adk-agent-builder\SKILL.md`

Use the `read_file` tool to review the current content of the skill, and then use the `replace` or `write_file` tool to update the "Personal Know-How Implementation" section with the new knowledge gathered from the release notes.

Always explain to the user what specific best practices were updated in the `adk-agent-builder` skill based on the new release.
