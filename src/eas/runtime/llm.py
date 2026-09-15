from __future__ import annotations

import os


class InvokeError(Exception):
    pass


def default_model() -> str:
    return os.environ.get("EAS_ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


def complete_agent(*, system: str, user: str, model: str | None = None) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise InvokeError(
            "ANTHROPIC_API_KEY is not set. Use --prepare and run the agent in your IDE, "
            "or set the key and pip install 'engineering-agent-system[llm]'."
        )

    model = model or default_model()

    try:
        import anthropic
    except ImportError as exc:
        raise InvokeError(
            "Optional LLM support not installed. Run: pip install 'engineering-agent-system[llm]'"
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    parts: list[str] = []
    for block in message.content:
        if block.type == "text":
            parts.append(block.text)
    if not parts:
        raise InvokeError("Empty response from model")
    return "\n".join(parts)
