
from typing import Literal
from pydantic import BaseModel, Field, model_validator


Task = Literal["generate", "debug", "explain"]

SUPPORTED_LANGUAGES = ["python", "java", "c", "c++", "sql"]


class LLMRequest(BaseModel):
    task: Task

    language: str = "python"

    user_input: str = ""

    code: str | None = None

    file_id: str | None = None

    error_message: str | None = None

    detail_level: Literal[
        "beginner", "intermediate", "advanced"
    ] = "beginner"

    rag_context: list[str] | str | None = None

    @model_validator(mode="after")
    def validate_request(self):

        if self.language.lower().strip() not in SUPPORTED_LANGUAGES:
            raise ValueError(
                "Supported languages: Python, Java, C, C++ and SQL"
            )

        if self.task == "generate":
            if not self.user_input.strip():
                raise ValueError("Coding request cannot be empty.")

        elif self.task in ("debug", "explain"):
            if not self.code or not self.code.strip():
                raise ValueError("Source code is required.")

        return self


class LLMResponse(BaseModel):
    task: Task
    language: str
    answer: str
    model: str
