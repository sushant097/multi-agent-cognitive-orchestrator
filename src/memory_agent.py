# src/agents/memory_agent.py
from __future__ import annotations

from typing import Any
from .base import Agent
from ..state import GlobalState


class MemoryAgent(Agent):
    """
    Maintains long-term memory and tool performance hints.
    """

    def __init__(self) -> None:
        super().__init__(name="memory")

    def run(self, state: GlobalState, **kwargs: Any) -> GlobalState:
        # Example: compute best tool by success rate, store as hint
        best_tool = None
        best_score = -1.0

        for tool_name, stats in state.tool_stats.items():
            score = stats.success_rate
            if score > best_score and stats.calls >= 3:  # need some data
                best_tool = tool_name
                best_score = score

        state.memory["preferred_tool"] = best_tool
        return state
