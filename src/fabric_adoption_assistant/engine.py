"""Deterministic assessment engine: no answer is ever inferred."""
from __future__ import annotations

from typing import Any

from .knowledge_base import get_definition, get_questions
from .models import (
    AssessmentInput,
    AssessmentReport,
    Disposition,
    WorkloadAssessment,
    WorkloadInput,
)

_SEVERITY = {
    Disposition.AS_IS: 0,
    Disposition.KEEP_OUTSIDE: 1,
    Disposition.OPTIMIZE: 2,
    Disposition.NEEDS_DISCOVERY: 3,
    Disposition.BLOCKED: 4,
}


def _matches(expected: dict[str, Any], answers: dict[str, Any]) -> bool:
    return all(key in answers and answers[key] == value for key, value in expected.items())


def _validate_answers(workload: WorkloadInput, questions: list[Any]) -> None:
    questions_by_id = {question.id: question for question in questions}
    unknown_ids = sorted(set(workload.answers) - set(questions_by_id))
    if unknown_ids:
        raise ValueError(
            f"Unknown answer ids for {workload.workload_type}: {', '.join(unknown_ids)}"
        )

    for answer_id, value in workload.answers.items():
        question = questions_by_id[answer_id]
        if question.answer_type == "choice" and value not in question.options:
            options = ", ".join(question.options)
            raise ValueError(f"Invalid value for {answer_id}: {value!r}. Expected one of: {options}")
        if question.answer_type == "boolean" and not isinstance(value, bool):
            raise ValueError(f"Invalid value for {answer_id}: expected a boolean")
        if question.answer_type == "number" and (
            isinstance(value, bool) or not isinstance(value, (int, float))
        ):
            raise ValueError(f"Invalid value for {answer_id}: expected a number")
        if question.answer_type == "text" and not isinstance(value, str):
            raise ValueError(f"Invalid value for {answer_id}: expected text")


def assess_workload(workload: WorkloadInput) -> WorkloadAssessment:
    definition = get_definition(workload.workload_type)
    questions = get_questions(workload.workload_type)
    _validate_answers(workload, questions)
    unanswered = [question for question in questions if question.required and question.id not in workload.answers]
    answered_required = len([question for question in questions if question.required and question.id in workload.answers])
    required_count = len([question for question in questions if question.required])
    confidence = round(answered_required / required_count * 100) if required_count else 100

    disposition = Disposition(definition["base_disposition"])
    blockers: list[str] = []
    actions: list[str] = []
    rationale: list[str] = []

    for rule in definition.get("rules", []):
        if not _matches(rule.get("when", {}), workload.answers):
            continue
        rule_disposition = Disposition(rule.get("disposition", disposition.value))
        if _SEVERITY[rule_disposition] > _SEVERITY[disposition]:
            disposition = rule_disposition
        blockers.extend(rule.get("blockers", []))
        actions.extend(rule.get("actions", []))
        rationale.extend(rule.get("rationale", []))

    limitations: list[str] = []
    if unanswered and disposition is not Disposition.BLOCKED:
        disposition = Disposition.NEEDS_DISCOVERY
        limitations.append(
            "No migration disposition is asserted until all required discovery questions are answered."
        )
    elif disposition is Disposition.NEEDS_DISCOVERY:
        limitations.append(
            "Required questions were answered, but a confirmed answer identifies unfinished discovery work."
        )
    if not workload.evidence:
        limitations.append(
            "No Microsoft Learn evidence snapshot is attached; validate recommendations before customer delivery."
        )

    return WorkloadAssessment(
        workload=workload,
        target_pattern=definition["target_pattern"],
        disposition=disposition,
        blockers=list(dict.fromkeys(blockers)),
        actions=list(dict.fromkeys(actions)),
        rationale=list(dict.fromkeys(rationale)),
        unanswered_questions=unanswered,
        evidence=workload.evidence,
        confidence_percent=confidence,
        limitations=limitations,
    )


def assess(intake: AssessmentInput) -> AssessmentReport:
    return AssessmentReport(
        customer_name=intake.customer_name,
        engagement_owner=intake.engagement_owner,
        business_outcomes=intake.business_outcomes,
        constraints=intake.constraints,
        assessments=[assess_workload(workload) for workload in intake.workloads],
    )
