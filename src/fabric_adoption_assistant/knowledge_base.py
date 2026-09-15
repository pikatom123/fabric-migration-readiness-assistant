"""Load and validate the versioned assessment knowledge base."""
from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Any

import yaml

from .models import Question


@lru_cache(maxsize=1)
def load_knowledge_base() -> dict[str, Any]:
    resource = files("fabric_adoption_assistant.data").joinpath("knowledge_base.yaml")
    raw = yaml.safe_load(resource.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not raw:
        raise ValueError("Knowledge base must contain workload definitions")
    return raw


def get_definition(workload_type: str) -> dict[str, Any]:
    knowledge = load_knowledge_base()
    if workload_type not in knowledge:
        supported = ", ".join(sorted(knowledge))
        raise KeyError(f"Unsupported workload type '{workload_type}'. Supported: {supported}")
    return knowledge[workload_type]


def get_questions(workload_type: str) -> list[Question]:
    return [Question.model_validate(item) for item in get_definition(workload_type)["questions"]]
