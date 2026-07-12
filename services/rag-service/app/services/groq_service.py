"""
Groq chat-completion wrapper with basic retry handling.
"""
import logging
import time

from groq import APIConnectionError, APIStatusError, APITimeoutError, Groq

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class GroqServiceError(Exception):
    """Raised when the Groq API call fails after retries."""


class GroqService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        if not self._settings.groq_api_key:
            logger.warning("GROQ_API_KEY is not set; LLM calls will fail.")
        self._client = Groq(
            api_key=self._settings.groq_api_key,
            timeout=self._settings.groq_timeout_s,
        )

    def chat(self, messages: list[dict[str, str]]) -> str:
        last_exc: Exception | None = None
        for attempt in range(1, self._settings.groq_max_retries + 2):
            try:
                completion = self._client.chat.completions.create(
                    model=self._settings.groq_model,
                    messages=messages,
                    temperature=self._settings.groq_temperature,
                    max_tokens=self._settings.groq_max_tokens,
                )
                choice = completion.choices[0]
                content = (choice.message.content or "").strip()
                if not content:
                    raise GroqServiceError("Groq returned an empty completion")
                return content
            except (APITimeoutError, APIConnectionError) as exc:
                last_exc = exc
                wait = min(2 ** attempt, 8)
                logger.warning(
                    "Groq call attempt %s failed (%s); retrying in %ss",
                    attempt,
                    exc,
                    wait,
                )
                time.sleep(wait)
            except APIStatusError as exc:
                logger.error("Groq API returned status error: %s", exc)
                raise GroqServiceError(f"Groq API error ({exc.status_code}): {exc.message}") from exc
            except Exception as exc:  # noqa: BLE001
                logger.exception("Unexpected error calling Groq")
                raise GroqServiceError(f"Unexpected Groq error: {exc}") from exc

        logger.error("Groq call failed after retries: %s", last_exc)
        raise GroqServiceError(f"Groq API unavailable after retries: {last_exc}")
