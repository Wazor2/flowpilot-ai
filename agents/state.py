from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ToolExecutionResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    status: str


class PlanStep(BaseModel):
    tool: str = Field(..., description="The name of the tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="The arguments for the tool")
    reason: str = Field(..., description="Reason for executing this tool")
    requires_approval: bool = Field(default=False, description="Whether this step requires human approval")


class State(BaseModel):
    workflow_id: str
    objective: str
    plan: List[PlanStep] = Field(default_factory=list)
    current_step_index: int = 0
    completed_actions: List[ToolExecutionResult] = Field(default_factory=list)
    failures: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "PLAN"
    replan_count: int = 0
    action_attempts: Dict[str, int] = Field(default_factory=dict)
    max_replans: int = Field(default_factory=lambda: int(__import__("os").getenv("MAX_REPLANS", "3")))
    max_execution_attempts_per_action: int = Field(
        default_factory=lambda: int(__import__("os").getenv("MAX_EXECUTION_ATTEMPTS_PER_ACTION", "2"))
    )
    pause_reason: str | None = None
