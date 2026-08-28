"""Task 4: Implement analyze_journal_entry using the OpenAI Responses API.

This project mandates the OpenAI Python SDK and a provider that supports the
Responses API, such as:
  - Microsoft Foundry Models
  - OpenAI proper

Set OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL in your .env file.
Settings are loaded by ``api.config.Settings``.
"""

import json
import logging

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

from api.config import get_settings


class AnalysisServiceError(Exception):
    """Base error for analysis failures."""


class AnalysisUnavailableError(AnalysisServiceError):
    """Upstream is rate-limited or temporarily down — safe to retry."""


class AnalysisFailedError(AnalysisServiceError):
    """Upstream or parsing failure that isn't retryable."""


def _default_client() -> AsyncOpenAI:
    """Construct the real OpenAI client from application settings.

    Called lazily from ``analyze_journal_entry`` so tests can inject a
    ``MockAsyncOpenAI`` without ever triggering this code path.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        timeout=30.0,
    )


def _is_retryable(exc: BaseException) -> bool:
    """Return True if the exception is retryable (rate limit, timeout, or server error)."""
    if isinstance(exc, APIStatusError):
        return exc.status_code == 429 or exc.status_code >= 500
    return isinstance(exc, (APITimeoutError, APIConnectionError))


def _response_refusal(response: object) -> str | None:
    """Return the model refusal message, if the response contains one."""
    for output_item in getattr(response, "output", []):
        for content_item in getattr(output_item, "content", []):
            refusal = getattr(content_item, "refusal", None)
            if refusal:
                return refusal
    return None


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client: AsyncOpenAI | None = None,
) -> dict:
    """Analyze a journal entry using the OpenAI Responses API.

    Args:
        entry_id: ID of the entry being analyzed (pass through to the result).
        entry_text: Combined work + struggle + intention text.
        client: OpenAI client. If None, a default one is constructed from
            application settings. Tests pass in a MockAsyncOpenAI here; production code
            in the router calls this with no ``client`` argument.

    Returns:
        A dict matching AnalysisResponse:
            {
                "entry_id":  str,
                "sentiment": str,   # "positive" | "negative" | "neutral"
                "summary":   str,
                "topics":    list[str],
            }

    TODO (Task 4):
      1. If ``client is None``, call ``_default_client()`` to construct one.
      2. Build an input that includes ``entry_text`` somewhere
         (the unit tests check that the entry text reaches the LLM).
      3. Call ``client.responses.create(...)`` with a model name
         (use ``get_settings().openai_model``).
      4. Parse ``response.output_text`` with ``json.loads()``.
      5. Return a dict with ``entry_id``, ``sentiment``, ``summary``, ``topics``.
    """
    if client is None:
        client = _default_client()

    try:
        async for attempt in AsyncRetrying(
            retry=retry_if_exception(_is_retryable),
            wait=wait_random_exponential(min=1, max=20),
            stop=stop_after_attempt(4),
            reraise=True,
        ):
            with attempt:
                response = await client.responses.create(
                    model=get_settings().openai_model,
                    instructions="Analyze the journal entry and provide a sentiment, summary, and topics.",
                    input=entry_text,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "analysis_response",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "sentiment": {
                                        "type": "string",
                                        "enum": ["positive", "negative", "neutral"],
                                    },
                                    "summary": {"type": "string"},
                                    "topics": {"type": "array", "items": {"type": "string"}},
                                },
                                "required": ["sentiment", "summary", "topics"],
                                "additionalProperties": False,
                            },
                            "strict": True,
                        },
                    },
                    max_output_tokens=500,
                )
    except APIStatusError as exc:
        logging.error("OpenAI API error %s: %s", exc.status_code, exc)
        if exc.status_code == 429 or exc.status_code >= 500:
            raise AnalysisUnavailableError() from exc
        raise AnalysisFailedError() from exc
    except (APITimeoutError, APIConnectionError) as exc:
        logging.error("OpenAI request timed out/unreachable: %s", exc)
        raise AnalysisUnavailableError() from exc

    refusal = _response_refusal(response)
    if refusal:
        logging.warning("Model refused entry %s: %s", entry_id, refusal)
        raise AnalysisFailedError() from RuntimeError(f"Model refused: {refusal}")

    output_text = response.output_text
    try:
        analysis_result = json.loads(output_text)
    except json.JSONDecodeError as exc:
        logging.error(
            "Failed to parse model output as JSON for entry %s: %s", entry_id, output_text
        )
        raise AnalysisFailedError() from exc

    return {
        "entry_id": entry_id,
        "sentiment": analysis_result.get("sentiment"),
        "summary": analysis_result.get("summary"),
        "topics": analysis_result.get("topics", []),
    }
