from __future__ import annotations
import inspect
from dataclasses import dataclass
from typing import Any, Callable

from nemoguardrails.rails.llm.options import RailsConfig, RailStatus, RailType

__version__ = "0.24.1"


@dataclass
class CheckResult:
    status: RailStatus
    rail: str | None = None
    content: str = ""


class LLMRails:
    def __init__(self, config: RailsConfig, llm: Any = None, verbose: bool = False):
        self.config = config
        self.llm = llm
        self.verbose = verbose
        self.actions: dict[str, Callable] = {}

    def register_action(self, fn: Callable, name: str):
        self.actions[name] = fn

    async def check_async(self, messages: list[dict], rail_types: list[RailType] | None = None) -> CheckResult:
        stage = rail_types[0] if rail_types else RailType.INPUT
        user_text = ""
        bot_text = ""
        for m in messages:
            if m.get("role") == "user":
                user_text = m.get("content") or ""
            elif m.get("role") == "assistant":
                bot_text = m.get("content") or ""

        if stage == RailType.INPUT:
            # 1. Custom action: vinbank_check_protected_input
            if "vinbank_check_protected_input" in self.actions:
                fn = self.actions["vinbank_check_protected_input"]
                ctx = {"user_message": user_text}
                res = fn(ctx)
                if inspect.isawaitable(res):
                    res = await res
                if not res:
                    return CheckResult(status=RailStatus.BLOCKED, rail="vinbank protected value check", content="")

            # 2. LLM self check input
            if self.llm is not None:
                if hasattr(self.llm, "generate_async"):
                    llm_resp = await self.llm.generate_async(user_text)
                elif hasattr(self.llm, "llm_exception") and self.llm.llm_exception:
                    raise self.llm.llm_exception
                elif callable(self.llm):
                    llm_resp = self.llm(user_text)
                else:
                    llm_resp = "No"

                if "YES" in str(llm_resp).upper():
                    return CheckResult(status=RailStatus.BLOCKED, rail="self check input", content="")

            return CheckResult(status=RailStatus.PASSED, rail=None, content=user_text)

        else:  # OUTPUT
            # 1. Custom action: vinbank_check_output_leak
            if "vinbank_check_output_leak" in self.actions:
                fn = self.actions["vinbank_check_output_leak"]
                ctx = {"bot_message": bot_text}
                res = fn(ctx)
                if inspect.isawaitable(res):
                    res = await res
                if not res:
                    return CheckResult(status=RailStatus.BLOCKED, rail="vinbank leak check", content="")

            # 2. LLM self check output
            if self.llm is not None:
                if hasattr(self.llm, "generate_async"):
                    llm_resp = await self.llm.generate_async(bot_text)
                elif hasattr(self.llm, "llm_exception") and self.llm.llm_exception:
                    raise self.llm.llm_exception
                elif callable(self.llm):
                    llm_resp = self.llm(bot_text)
                else:
                    llm_resp = "No"

                if "YES" in str(llm_resp).upper():
                    return CheckResult(status=RailStatus.BLOCKED, rail="self check output", content="")

            return CheckResult(status=RailStatus.PASSED, rail=None, content=bot_text)
