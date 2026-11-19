from __future__ import annotations
from typing import Any


class FakeLLMModel:
    def __init__(self, responses: list[str] | None = None, llm_exception: Exception | None = None):
        self.responses = list(responses or [])
        self.llm_exception = llm_exception

    async def generate_async(self, prompt: str = "") -> str:
        if self.llm_exception is not None:
            raise self.llm_exception
        if self.responses:
            return self.responses.pop(0)
        return "No"

    def __call__(self, *args, **kwargs) -> str:
        if self.llm_exception is not None:
            raise self.llm_exception
        if self.responses:
            return self.responses.pop(0)
        return "No"
