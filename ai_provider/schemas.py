from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Constraint(BaseModel):
    field: str
    operator: str
    value: str | float | int


class BusinessObjective(BaseModel):
    objective_id: str
    original_request: str
    goal: str
    entities: list[str] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    required_information: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    approval_sensitive_actions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    step_id: str
    description: str
    tool: str
    input_requirements: dict = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    expected_output: str
    requires_approval: bool = False


class ExecutionPlan(BaseModel):
    plan_id: str
    objective_id: str
    steps: list[PlanStep]


class ActionRecommendation(BaseModel):
    invoice_id: Optional[str] = None
    priority: str  # e.g. "LOW" | "MEDIUM" | "HIGH"
    recommended_action: str
    reasoning_summary: str
    evidence: list[str] = Field(default_factory=list)
    policy_rules_triggered: list[str] = Field(default_factory=list)
    approval_required: bool = True
