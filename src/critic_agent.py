# src/agents/critic_agent.py
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

        max_retries = state.constraints.get("max_retries", 3)

        if step.status == "failed" and step.attempts >= max_retries:
            # Trigger human-in-loop for this step
            state.flags["need_human_for_step"] = step.id
            state.flags["plan_rewrite_needed"] = True
        elif step.status == "failed":
            # allow executor to retry via coordinator
            state.flags["should_retry_step"] = True
        else:
            # Clear flags if success
            state.flags.pop("should_retry_step", None)
            state.flags.pop("need_human_for_step", None)

        # Simple heuristic: if final_answer is set, we can stop
        if state.final_answer:
            state.session_status = "done"

        return state
