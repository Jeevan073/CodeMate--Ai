
import os
import time
import logging
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError

from .prompts import SYSTEM_PROMPTS, build_prompt
from app.rag.retriever import CodeRetriever


# Load environment variables
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

        self.api_key = os.getenv("OPENROUTER_API_KEY")

        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "openrouter/free"
        )

        self.client = None

        # Initialize RAG retriever
        self.retriever = CodeRetriever()

    def _get_client(self):

        if not self.api_key:
            raise LLMServiceError(
                "OpenRouter API key is missing in .env"
            )

        if self.client is None:

            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1",
                    default_headers={
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "CodeMate AI"
                    }
                )

            except Exception as exc:

                logger.exception(
                    "OpenRouter initialization failed"
                )

                raise LLMServiceError(
                    "Unable to initialize OpenRouter."
                ) from exc

        return self.client

    def respond(self, request):

        try:
            # Retrieve relevant documentation
            query_parts = [
                request.user_input or "",
                request.code or "",
                request.error_message or ""
            ]

            query = "\n".join(
                part for part in query_parts if part.strip()
            )

            if query:
                retrieved_chunks = self.retriever.retrieve(
                    query=query,
                    language=request.language,
                    top_k=5
                )

                # Convert retrieved chunks into prompt context
                request.rag_context = [
                    chunk["text"]
                    for chunk in retrieved_chunks
                ]

                logger.info(
                    "RAG retrieved %d chunks",
                    len(retrieved_chunks)
                )
                print(f"CODEMATE RAG: Retrieved {len(retrieved_chunks)} chunks")

        except Exception as exc:
            # Keep LLM working even if RAG retrieval fails
            logger.exception("RAG retrieval failed")
            request.rag_context = None

        # Build prompt after retrieving context
        prompt = build_prompt(request)
        print("CODEMATE RAG CONTEXT INCLUDED:", "Documentation 1:" in prompt)
        print("PROMPT LENGTH:", len(prompt))

        client = self._get_client()

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPTS[request.task]
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        for attempt in range(MAX_RETRIES):

            try:

                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2
                )

                answer = response.choices[0].message.content

                if not answer or not answer.strip():

                    raise LLMServiceError(
                        "OpenRouter returned an empty response."
                    )

                return answer.strip()

            except LLMServiceError:
                raise

            except Exception as exc:

                status = getattr(
                    exc,
                    "status_code",
                    getattr(exc, "code", None)
                )

                retryable = (
                    status in RETRYABLE_STATUS_CODES
                    or isinstance(exc, APIConnectionError)
                )

                if not retryable or attempt == MAX_RETRIES - 1:

                    logger.exception(
                        "OpenRouter request failed"
                    )

                    if status == 401:
                        raise LLMServiceError(
                            "Invalid OpenRouter API key."
                        ) from exc

                    if status == 402:
                        raise LLMServiceError(
                            "OpenRouter requires credits for this request. "
                            "Check that you selected a free model."
                        ) from exc

                    if status == 429:
                        raise LLMServiceError(
                            "OpenRouter rate limit exceeded. Try again later."
                        ) from exc

                    if retryable:
                        raise LLMServiceError(
                            "OpenRouter is temporarily unavailable."
                        ) from exc

                    raise LLMServiceError(
                        "OpenRouter request failed. Check API key, "
                        "model, internet and provider availability."
                    ) from exc

                delay = 2 ** attempt

                logger.warning(
                    "Retrying OpenRouter request in %s seconds",
                    delay
                )

                time.sleep(delay)


# Shared reusable service

llm_service = LLMService()
