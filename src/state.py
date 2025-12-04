# src/state.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal
import time
import uuid


StatusType = Literal["pending", "running", "success", "failed", "skipped"]
SessionStatus = Literal["running", "done", "failed"]


def _now_ts() -> float:
    return time.time()


@dataclass
class ToolCallRecord:
    tool_name: str
    success: bool
    latency_ms: float
    error: Optional[str] = None
    timestamp: float = field(default_factory=_now_ts)


@dataclass
class ToolStats:
    calls: int = 0
    successes: int = 0
    failures: int = 0
    total_latency_ms: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        if self.calls == 0:
            return 0.0
        return self.total_latency_ms / self.calls

    @property
    def success_rate(self) -> float:
        if self.calls == 0:
            return 0.0
        return self.successes / self.calls


@dataclass
class PlanStep:
    id: str
    description: str
    agent: str  # "perception", "retriever", "executor", ...
    tool_name: Optional[str] = None
    input: Optional[Any] = None
    output: Optional[Any] = None
    status: StatusType = "pending"
    error: Optional[str] = None
    attempts: int = 0

    @staticmethod
    def create(
        description: str,
        agent: str,
        tool_name: Optional[str] = None,
        input: Optional[Any] = None,
    ) -> "PlanStep":
        return PlanStep(
            id=str(uuid.uuid4())[:8],
            description=description,
            agent=agent,
            tool_name=tool_name,
            input=input,
        )


@dataclass
class GlobalState:
    # High-level
    query: str
    objective: Optional[str] = None
    entities: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)

    # Plan + execution
    plan: List[PlanStep] = field(default_factory=list)
    current_step_index: int = 0
    session_status: SessionStatus = "running"

    # Memory + history
    memory: Dict[str, Any] = field(default_factory=dict)
    history: List[PlanStep] = field(default_factory=list)

    # Tool performance
    tool_stats: Dict[str, ToolStats] = field(default_factory=dict)
    tool_log: List[ToolCallRecord] = field(default_factory=list)

    # Flags & meta
    flags: Dict[str, Any] = field(default_factory=dict)
    final_answer: Optional[str] = None

    def current_step(self) -> Optional[PlanStep]:
        if 0 <= self.current_step_index < len(self.plan):
            return self.plan[self.current_step_index]
        return None

    def add_tool_record(self, record: ToolCallRecord) -> None:
        self.tool_log.append(record)
        stats = self.tool_stats.setdefault(record.tool_name, ToolStats())
        stats.calls += 1
        stats.total_latency_ms += record.latency_ms
        if record.success:
            stats.successes += 1
        else:
            stats.failures += 1

    def mark_done(self, answer: Optional[str] = None) -> None:
        self.session_status = "done"
        if answer is not None:
            self.final_answer = answer

    def mark_failed(self, reason: Optional[str] = None) -> None:
        self.session_status = "failed"
        if reason:
            self.flags["failure_reason"] = reason
