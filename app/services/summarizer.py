from __future__ import annotations

from dataclasses import dataclass

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from app.core.config import settings


@dataclass(frozen=True)
class LLMError(Exception):
    code: str


def summarize(text: str, *, max_chars: int = 500) -> str:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return ""

    if not settings.openai_api_key:
        return cleaned

    client = OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        max_retries=0,
    )
    try:
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Summarize the input text clearly and briefly."},
                {"role": "user", "content": cleaned},
            ],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except APITimeoutError as e:
        raise LLMError("llm_timeout") from e
    except (AuthenticationError, RateLimitError) as e:
        raise LLMError("llm_unavailable") from e
    except APIConnectionError as e:
        raise LLMError("llm_connection_error") from e
    except Exception as e:
        raise LLMError("llm_error") from e

