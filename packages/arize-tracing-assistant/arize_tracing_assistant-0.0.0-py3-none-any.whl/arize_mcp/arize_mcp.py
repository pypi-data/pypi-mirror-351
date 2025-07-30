from mcp.server.fastmcp import FastMCP  # type: ignore
from pathlib import Path
import os
import requests
import json

mcp = FastMCP("Arize-MCP-Tracing-Assistant")

LANG_MAP = {
    "python": "python",
    "py": "python",
    "javascript": "typescript",
    "js": "typescript",
    "typescript": "typescript",
    "ts": "typescript",
}


FRAMEWORK_MAP = {
    "agno": "agno",
    "amazon-bedrock": "amazon-bedrock",
    "aws-bedrock": "amazon-bedrock",
    "aws-bedrock-agents": "amazon-bedrock",
    "bedrock": "amazon-bedrock",
    "anthropic": "anthropic",
    "autogen": "autogen",
    "beeai": "beeai",
    "crewai": "crewai",
    "dspy": "dspy",
    "google-gen-ai": "google-gen-ai",
    "google-genai": "google-gen-ai",
    "groq": "groq",
    "guardrails-ai": "guardrails-ai",
    "guardrails": "guardrails-ai",
    "haystack": "haystack",
    "hugging-face-smolagents": "hugging-face-smolagents",
    "smolagents": "hugging-face-smolagents",
    "instructor": "instructor",
    "langchain": "langchain",
    "langflow": "langflow",
    "langgraph": "langgraph",
    "litellm": "litellm",
    "llamaindex": "llamaindex",
    "llama-index": "llamaindex",
    "llamaindex-workflows": "llamaindex",
    "llama-index-workflows": "llamaindex",
    "mistralai": "mistralai",
    "model-context-protocol": "model-context-protocol",
    "openai": "openai",
    "open-ai": "openai",
    "openai-agents": "openai-agents",
    "prompt-flow": "prompt-flow",
    "together": "together",
    "together-ai": "together",
    "togetherai": "together",
    "vercel": "vercel",
    "vertexai": "vertexai",
    "vertex-ai": "vertexai",
    "vertex": "vertexai",
}

PROMPT_ARIZE = """
You are about to receive code snippets that demonstrate how to export OpenTelemetry/OpenInference traces either AUTOMATICALLY (framework-specific) or MANUALLY (framework-agnostic).

• Arize ⟶ commercial SaaS built on OpenTelemetry / OpenInference  
• Phoenix ⟶ open-source sibling; identical ingestion format  
• Auto-instrumentation = framework-specific, minimal code  
• Manual instrumentation = framework-agnostic, maximum control

```txt
=== AUTO INSTRUMENTATION EXAMPLE ({framework}) ===
{auto_inst_example}

=== MANUAL INSTRUMENTATION EXAMPLE 1: SEND TRACES ===
{send_traces_example}

=== MANUAL INSTRUMENTATION EXAMPLE 2: SEND TRACES FROM AN STREAMLIT APP ===
{manual_inst_example}
```
"""


PROMPT_PHOENIX = """
You are about to receive code snippets that demonstrate how to export OpenTelemetry/OpenInference traces either AUTOMATICALLY (framework-specific) or MANUALLY (framework-agnostic).

• Arize = commercial AI observability platform built on OpenTelemetry / OpenInference  
• Phoenix =open-source sibling; almost identical ingestion format  
• Auto instrumentation = framework-specific open inference instrumentors, minimal code  
• Manual instrumentation = framework-agnostic, maximum control, more code

```txt
=== PHOENIX SETUP ===
{phoenix_setup}

=== AUTO INSTRUMENTATION EXAMPLE ({framework}) ===
{auto_inst_example}

=== MANUAL INSTRUMENTATION EXAMPLE 1: SEND TRACES ===
{send_traces_example}

=== MANUAL INSTRUMENTATION EXAMPLE 2: SEND TRACES FROM AN STREAMLIT APP ===
{manual_inst_example}
```
"""


ROOT = Path(__file__).resolve().parents[0]
EXAMPLES_DIR = ROOT / "auto_inst_examples"


def normalize_lang(lang: str) -> str:
    return LANG_MAP.get(lang.lower(), "python")  # Default to Python if not found


def normalize_framework(framework: str) -> str:
    return FRAMEWORK_MAP.get(
        framework.replace("_", "-").lower(), "openai"
    )  # Default to OpenAI if not found


def get_manual_tracing_examples(product: str) -> str:
    """
    Get manual instrumentation examples for Arize or Phoenix. Defaults to Arize.
    """

    if product not in ["arize", "phoenix"]:
        product = "arize"

    manual_dir = ROOT / "manual_inst_examples"

    file_name = f"app_manually_instrumented_{product}.md"
    path = manual_dir / file_name

    if not path.exists():
        path = manual_dir / "app_manually_instrumented_arize.md"

    return path.read_text(encoding="utf-8")


def get_send_traces_examples(product: str) -> str:
    """
    Get send traces examples for Arize or Phoenix. Defaults to Arize.
    """

    if product not in ["arize", "phoenix"]:
        product = "arize"

    manual_dir = ROOT / "manual_inst_examples"

    file_name = f"send_traces_{product}.md"
    path = manual_dir / file_name

    if not path.exists():
        path = manual_dir / "send_traces_arize.md"

    return path.read_text(encoding="utf-8")


def get_auto_tracing_example(product: str, framework: str, language: str) -> str:
    """
    Get auto instrumentation examples for Arize or Phoenix. Defaults to Arize
    """
    lang = normalize_lang(language)
    framework = normalize_framework(framework)  # type: ignore

    path = EXAMPLES_DIR / product / framework / f"{lang}.md"

    if not path.exists():
        return (
            "Examples not found for the given framework/language combination. Defaulting to python and openai"
            "Please ensure you provide a valid pair or use manual instrumentation with open telemetry."
        )
    return path.read_text(encoding="utf-8")


def send_sync_runllm_request(
    assistant_id: str,
    api_key: str,
    message: str,
) -> str:
    """
    Send a request to the streaming API and **return the full response as a string**.

    Args:
        assistant_id (str): ID from https://app.runllm.com/assistant/NNN
        api_key (str): RunLLM API key.
        message (str): User message for the assistant.

    Returns:
        str: The complete assistant response.
    """
    url = RUNLLM_URL.format(assistant_id=assistant_id)
    headers = {
        "cors": "no-cors",
        "Access-Control-Allow-Origin": "*",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    body = {"message": message, "source": "web"}

    full_response = ""
    with requests.post(url, headers=headers, json=body, stream=True) as response:
        if response.status_code != 200:
            raise RuntimeError(f"Request failed with status {response.status_code}")

        for line in response.iter_lines():
            if not line:
                continue

            try:
                # Remove SSE prefix and decode JSON
                data = json.loads(line.decode("utf-8").lstrip("data: "))
                full_response += data.get("content", "")
            except json.JSONDecodeError as exc:
                print(f"[send_runllm_request] JSON decode error: {exc}")

    return full_response


@mcp.tool()
def get_arize_tracing_example(framework: str, language: str) -> str:
    """
    Get examples to instrument an app and send traces/spans to Arize.
    If the framework is not in the list use manual instrumentation with open telemetry.

    Parameters
    ----------
    framework : str
        LLM provider or framework. One of:
        ["agno", "amazon-bedrock", "anthropic", "autogen", "beeai", "crewai", "dspy", "google-gen-ai", "groq", "guardrails-ai", "haystack",
        "hugging-face-smolagents", "instructor", "langchain", "langflow", "langgraph", "litellm", "llamaindex", "mistralai", "openai", "openai-agents", "prompt-flow",
        "together", "vercel", "vertexai"]
    language : str
        Programming language: "python" or "typescript". Defaults to "python".

    Returns
    -------
    str
        Example code snippets for auto/manual instrumentation for Arize.
    """
    auto_inst_example = get_auto_tracing_example("arize", framework, language)
    manual_inst_example = get_manual_tracing_examples("arize")
    send_traces_example = get_send_traces_examples("arize")

    return PROMPT_ARIZE.format_map(
        {
            "auto_inst_example": auto_inst_example,
            "framework": framework,
            "send_traces_example": send_traces_example,
            "manual_inst_example": manual_inst_example,
        }
    )


@mcp.tool()
def get_phoenix_tracing_example(framework: str, language: str) -> str:
    """
    Get examples to instrument an app and send traces/spans to Phoenix.
    If the framework is not in the list use manual instrumentation with open telemetry.

    Parameters
    ----------
    framework : str
        LLM provider or framework. One of:
        ["agno", "amazon-bedrock", "anthropic", "autogen", "beeai", "crewai", "dspy", "google-gen-ai", "groq", "guardrails-ai", "haystack",
        "hugging-face-smolagents", "instructor", "langchain", "langflow", "langgraph", "litellm", "llamaindex", "mistralai", "openai", "openai-agents", "prompt-flow",
        "together", "vercel", "vertexai"]
    language : str
        Programming language: "python" or "typescript". Defaults to "python".

    Returns
    -------
    str
        Example code snippets for auto/manual instrumentation for Phoenix.
    """
    auto_inst_example = get_auto_tracing_example("phoenix", framework, language)
    manual_inst_example = get_manual_tracing_examples("phoenix")
    send_traces_example = get_send_traces_examples("phoenix")

    setup_path = EXAMPLES_DIR / "phoenix" / "phoenix_setup.md"
    phoenix_setup = setup_path.read_text(encoding="utf-8")

    return PROMPT_PHOENIX.format_map(
        {
            "phoenix_setup": phoenix_setup,
            "auto_inst_example": auto_inst_example,
            "framework": framework,
            "manual_inst_example": manual_inst_example,
            "send_traces_example": send_traces_example,
        }
    )


RUNLLM_URL = "https://api.runllm.com/api/pipeline/{assistant_id}/chat"
RUNLLM_API_KEY = os.environ.get("RUNLLM_API_KEY", None)

if RUNLLM_API_KEY == "###" or RUNLLM_API_KEY == "":
    RUNLLM_API_KEY = None

ASSISTANT_ID = "938"

if RUNLLM_API_KEY:

    @mcp.tool()
    def ask_question_about_tracing(question: str) -> str:
        """Ask a question about sending traces or instrumenting Arize or Phoenix, this function will answer based on the most uptodate documentation.
        Before calling this tool try to figure out the answer by getting tracing examples."""
        return send_sync_runllm_request(
            assistant_id=ASSISTANT_ID,
            api_key=RUNLLM_API_KEY,  # type: ignore
            message=question,
        )


if __name__ == "__main__":
    mcp.run(transport="stdio")
