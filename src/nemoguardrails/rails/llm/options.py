from __future__ import annotations
from typing import Any
from types import SimpleNamespace
from enum import Enum


class RailStatus(str, Enum):
    PASSED = "passed"
    BLOCKED = "blocked"


class RailType(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class ModelEntry:
    def __init__(self, data: dict):
        self.type = data.get("type")
        self.engine = data.get("engine")
        self.model = data.get("model")
        self.api_key_env_var = data.get("api_key_env_var")
        self.parameters = data.get("parameters") or {}


class PromptEntry:
    def __init__(self, data: dict):
        self.task = data.get("task")
        self.content = data.get("content")


class RailsConfig:
    def __init__(self, colang_content: str, config: dict):
        self.colang_content = colang_content
        self.raw_config = config
        self.models = [ModelEntry(m) for m in config.get("models", [])]
        self.prompts = [PromptEntry(p) for p in config.get("prompts", [])]
        rails_data = config.get("rails", {})
        self.rails = SimpleNamespace(
            input=SimpleNamespace(flows=rails_data.get("input", {}).get("flows", [])),
            output=SimpleNamespace(flows=rails_data.get("output", {}).get("flows", [])),
        )

    @classmethod
    def from_content(cls, colang_content: str, config: dict) -> RailsConfig:
        return cls(colang_content, config)
