"""Render customer-ready HTML from the deterministic assessment output."""
from __future__ import annotations

from datetime import date
from importlib.resources import files

from jinja2 import Environment

from .models import AssessmentReport, Disposition


def render_html(report: AssessmentReport) -> str:
    template_path = files("fabric_adoption_assistant").joinpath("templates/report.html.j2")
    environment = Environment(autoescape=True)
    template = environment.from_string(template_path.read_text(encoding="utf-8"))
    counts = {disposition.value: 0 for disposition in Disposition}
    for assessment in report.assessments:
        counts[assessment.disposition.value] += 1
    evidence_count = sum(len(assessment.evidence) for assessment in report.assessments)
    average_confidence = (
        round(sum(item.confidence_percent for item in report.assessments) / len(report.assessments))
        if report.assessments
        else 0
    )
    return template.render(
        report=report,
        counts=counts,
        evidence_count=evidence_count,
        average_confidence=average_confidence,
        generated_on=date.today().isoformat(),
    )
