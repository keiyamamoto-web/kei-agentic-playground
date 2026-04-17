---
name: adk-agent-builder
description: Use this skill to apply personal ADK know-how, best practices, and workarounds discovered during project development.
---

# ADK Personal Know-How & Best Practices

This skill contains specific knowledge, workarounds, and best practices discovered while developing ADK agents in this workspace. When building or debugging agents, refer to these points in addition to the official ADK documentation.

## Personal Know-How Implementation

*   **Tools**: Recommend using simple async functions (`async def`) instead of `BaseTool` subclasses to avoid registration issues.
*   **Artifacts**: When generating files (images, PDFs), use `tool_context.save_artifact` instead of session state.
*   **Retries**: Configure `http_options` in `GenerateContentConfig` for API calls to handle 429 errors.
*   **MCP**: Use `StreamableHTTPConnectionParams` for connecting to remote MCP servers.
*   **Tool Parameter Validation**: When using Pydantic `BaseModel` parameters in tools, be aware that `FunctionTool` correctly populates "required" fields, so ensure your models are explicitly typed.
*   **Tool Output Formatting**: For tools returning stdout/stderr, handle `'<No stdout/stderr captured>'` instead of assuming empty strings `""` when no output is produced.
*   **Dependencies**: Explicitly specify versions like `google-adk>=1.28.0` and `google-genai>=1.64.0` in the `requirements.txt` to ensure stability and compatibility with newer features.
*   **BigQuery Table Names**: When running PowerShell commands via `run_shell_command` with BigQuery, use triple backticks (```) around fully qualified table names containing dashes (e.g., ```matsubara-lab.region-us.INFORMATION_SCHEMA.RESERVATIONS```) to correctly escape characters in `bq query`.
*   **Agent Engine Deployment**: Avoid installing heavy data science packages like pandas, matplotlib, or seaborn in `requirements.txt`. They can cause OOM errors or setuptools conflicts leading to silent crashes (`no valid RunAgentResponse from stream data of size 0`).
