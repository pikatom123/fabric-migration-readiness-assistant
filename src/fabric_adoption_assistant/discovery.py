"""Knowledge-driven helpers for a conversational discovery experience."""
from __future__ import annotations

from typing import Any

from .knowledge_base import get_definition, get_questions, load_knowledge_base
from .models import Question


def supported_workloads() -> list[dict[str, str]]:
    return [
        {"id": workload_type, "label": definition["label"]}
        for workload_type, definition in load_knowledge_base().items()
    ]


def next_questions(
    workload_type: str,
    answers: dict[str, Any] | None = None,
    *,
    limit: int = 3,
) -> list[Question]:
    """Return the next unanswered questions without inventing defaults."""
    known_answers = answers or {}
    return [
        question
        for question in get_questions(workload_type)
        if question.id not in known_answers
    ][:limit]


def discovery_progress(workload_type: str, answers: dict[str, Any] | None = None) -> dict[str, Any]:
    known_answers = answers or {}
    questions = get_questions(workload_type)
    answered = len([question for question in questions if question.id in known_answers])
    return {
        "workload_type": workload_type,
        "label": get_definition(workload_type)["label"],
        "answered": answered,
        "total": len(questions),
        "complete": answered == len(questions),
        "next_questions": [question.model_dump() for question in next_questions(workload_type, known_answers)],
        "docs_query": get_definition(workload_type)["docs_query"],
    }
