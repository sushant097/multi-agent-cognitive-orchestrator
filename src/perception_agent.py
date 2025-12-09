
from __future__ import annotations

from typing import Any, Dict
from .base import Agent
from ..state import GlobalState


class PerceptionAgent(Agent):
    """
    Turns raw query / step output into structured objective, entities, constraints.
    """

    def __init__(self) -> None:
        super().__init__(name="perception")

    def run(self, state: GlobalState, **kwargs: Any) -> GlobalState:
        # TODO: Replace this heuristic logic with an LLM call if you want.
        query = state.query.lower()

        entities: list[str] = []
        if " vs " in query:
            entities = [p.strip() for p in query.split(" vs ")]

        state.entities = entities
        state.objective = state.objective or f"Answer the user's query: {state.query}"
        state.constraints.setdefault("max_steps", 3)
        state.constraints.setdefault("max_retries", 3)
        return state
