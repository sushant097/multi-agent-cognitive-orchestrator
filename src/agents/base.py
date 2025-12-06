# src/agents/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from ..state import GlobalState


class Agent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def run(self, state: GlobalState, **kwargs: Any) -> GlobalState:
        """Read + update GlobalState. Must be side-effect free except for state changes."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<Agent name={self.name}>"
