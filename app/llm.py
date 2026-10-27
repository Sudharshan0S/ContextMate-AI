import logging
import time

from google import genai
from google.genai import types
from google.genai import errors as genai_errors

from app.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    MAX_HISTORY_MESSAGES,
    MAX_RETRIES,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

_client = None

RETRYABLE_CODES = {429, 500, 502, 503, 504}


def get_client():
    global _client

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    if _client is None:
        _client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=30000),
        )

    return _client


def generate_reply(history, user_message: str) -> str:
    client = get_client()

    contents = []

    # Only use the recent conversation context.
    recent_history = history[-MAX_HISTORY_MESSAGES:]

    # Gemini expects user/model roles, not user/assistant.
    for message in recent_history:
        role = (
            "model"
            if message["role"] == "assistant"
            else "user"
        )

        contents.append(
            types.Content(
                role=role,
                parts=[
                    types.Part.from_text(
                        text=message["content"]
                    )
                ],
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "Gemini request started: attempt %s/%s",
                attempt,
                MAX_RETRIES,
            )

            start_time = time.perf_counter()

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )

            elapsed = time.perf_counter() - start_time
            logger.info(
                "Gemini response received in %.2f seconds",
                elapsed,
            )

            if not response.text or not response.text.strip():
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except genai_errors.APIError as error:
            status = getattr(error, "code", None)

            logger.warning(
                "Gemini API error on attempt %s: status=%s",
                attempt,
                status,
            )

            if (
                status not in RETRYABLE_CODES
                or attempt == MAX_RETRIES
            ):
                raise

            # Wait 1 second, then 2 seconds before retrying.
            time.sleep(2 ** (attempt - 1))

        except Exception:
            logger.exception("Unexpected Gemini error.")
            raise

    raise RuntimeError("Gemini request failed after retries.")