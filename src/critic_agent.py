# src/critic_agent.py
from __future__ import annotations

from typing import Any
from .base import Agent
from ..state import GlobalState


class CriticAgent(Agent):
    """
    Evaluates last step and decides if plan rewrite or human-in-loop is needed.
    """

    def __init__(self) -> None:
        super().__init__(name="critic")

    def run(self, state: GlobalState, **kwargs: Any) -> GlobalState:
        step = state.current_step()
        if not step:
            return state

        raw_max_retries = state.constraints.get("max_retries", 3)
        try:
            max_retries = int(raw_max_retries)
        except (TypeError, ValueError):
            max_retries = 3

        if step.status == "failed" and step.attempts >= max_retries:
            # Trigger human-in-loop for this step
            state.flags["need_human_for_step"] = step.id
            state.flags["plan_rewrite_needed"] = True
            state.flags.pop("should_retry_step", None)
        elif step.status == "failed":
            # allow executor to retry via coordinator
            state.flags["should_retry_step"] = True
            state.flags.pop("plan_rewrite_needed", None)
        else:
            # Clear flags if success
            state.flags.pop("should_retry_step", None)
            state.flags.pop("need_human_for_step", None)
            state.flags.pop("plan_rewrite_needed", None)

        # Simple heuristic: if final_answer is set, we can stop
        if state.final_answer:
            state.session_status = "done"

        return state
