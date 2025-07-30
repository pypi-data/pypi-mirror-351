# Arize Tracing Assistant

## Overview

This MCP server provides your LLM with examples of how to instrument your AI apps with Arize or Phoenix.
Connect it to your IDE or LLM and get curated tracing examples, setup guides and best practices.
If you have a `RUNLLM_API_KEY`, add it to your environment and the *ask_question_about_tracing* tool will be exposed. This key is not required for the MCP to work.

---

## Installation

Make sure **uv** (the fast Python package manager) is installed on your system. Installation instructions: [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer).

  - On macOS:
    ```bash
    brew install uv
    ```
  - On Linux:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | less
    ```
  - On Windows:
    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | more"
    ```

### Cursor

1. Go to Cursor Settings > MCP.
2. Click "Add new global MCP server" and add the server to your config JSON.
3. Remove the `env` section if you don't have access to RunLLM.

Example config:

```json
"arize-tracing-assistant": {
  "command": "uvx",
  "args": [
    "arize-tracing-assistant"
  ],
  "env": {
    "RUNLLM_API_KEY": "###"
  }
}
```

---

### Claude Desktop

1. Go to Claude Desktop Settings.
2. In Developer > Edit Config and add this to your config JSON:

```json
"arize-tracing-assistant": {
  "command": "/Users/myuser/miniconda3/bin/uvx",
  "args": [
   "arize-tracing-assistant"
  ],
  "env": {
    "RUNLLM_API_KEY": "###"
  }
}
```

---

## Troubleshooting

- Make sure the JSON configs are perfectly formatted.
- Clear the **uv** cache with `uv cache clean` to access the latest version.
- Make sure your `uv` command is pointing to the right location by running `which uv`, or simply use the full path.
- The server should start in the terminal just by running:

  ```bash
  uvx arize-tracing-assistant
  ```
- Use the Anthropic MCP inspector by running:
  ```bash
  npx @modelcontextprotocol/inspector uvx arize-tracing-assistant
  ```
