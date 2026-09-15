"""Validated input and output contracts for readiness assessments."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Disposition(str, Enum):
    AS_IS = "As-Is"
    OPTIMIZE = "Needs Optimisation"
    BLOCKED = "Blocked / Redesign Required"
    KEEP_OUTSIDE = "Keep Outside Fabric"
    NEEDS_DISCOVERY = "Needs Discovery"


class EvidenceSource(BaseModel):
    title: str
    url: HttpUrl
    claim: str
    retrieved_on: date


class WorkloadInput(BaseModel):
    name: str = Field(min_length=1)
    workload_type: str
    size_gb: float | None = Field(default=None, ge=0)
    answers: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
    evidence: list[EvidenceSource] = Field(default_factory=list)


class AssessmentInput(BaseModel):
    customer_name: str = Field(min_length=1)
    engagement_owner: str | None = None
    business_outcomes: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    workloads: list[WorkloadInput] = Field(default_factory=list)


class Question(BaseModel):
    id: str
    prompt: str
    answer_type: str = "text"
    required: bool = True
    options: list[str] = Field(default_factory=list)


class WorkloadAssessment(BaseModel):
    workload: WorkloadInput
    target_pattern: str
    disposition: Disposition
    blockers: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    rationale: list[str] = Field(default_factory=list)
    unanswered_questions: list[Question] = Field(default_factory=list)
    evidence: list[EvidenceSource] = Field(default_factory=list)
    confidence_percent: int = Field(ge=0, le=100)
    limitations: list[str] = Field(default_factory=list)


class AssessmentReport(BaseModel):
    customer_name: str
    engagement_owner: str | None = None
    business_outcomes: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assessments: list[WorkloadAssessment]
