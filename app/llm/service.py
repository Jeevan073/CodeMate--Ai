import os
import time
import logging
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .prompts import SYSTEM_PROMPTS, build_prompt


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

RETRYABLE_STATUS_CODES = {
    429, 500, 502, 503, 504
}


class LLMServiceError(Exception):
    pass


class LLMService:

    def __init__(self):

        self.api_key = os.getenv("GEMINI_API_KEY")

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        self.client = None

    def _get_client(self):

        if not self.api_key:
            raise LLMServiceError(
                "Gemini API key is missing in .env"
            )

        if self.client is None:

            try:
                self.client = genai.Client(
                    api_key=self.api_key
                )

            except Exception as exc:
                logger.exception("Gemini initialization failed")

                raise LLMServiceError(
                    "Unable to initialize Gemini."
                ) from exc

        return self.client

    def respond(self, request):

        prompt = build_prompt(request)

        client = self._get_client()

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPTS[request.task],
            temperature=0.2
        )

        for attempt in range(MAX_RETRIES):

            try:

                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )

                answer = response.text

                if not answer or not answer.strip():

                    raise LLMServiceError(
                        "Gemini returned an empty response."
                    )

                return answer.strip()

            except LLMServiceError:
                raise

            except Exception as exc:

                status = getattr(exc, "code", None)

                if (
                    status not in RETRYABLE_STATUS_CODES
                    or attempt == MAX_RETRIES - 1
                ):

                    logger.exception("Gemini request failed")

                    if status in RETRYABLE_STATUS_CODES:
                        raise LLMServiceError(
                            "Gemini is temporarily unavailable."
                        ) from exc

                    raise LLMServiceError(
                        "Gemini request failed. Check API key, "
                        "model, internet and quota."
                    ) from exc

                delay = 2 ** attempt

                logger.warning(
                    "Retrying Gemini request in %s seconds",
                    delay
                )

                time.sleep(delay)


# Shared reusable service

llm_service = LLMService()