"""Command-line boundary used by Copilot skills and automation."""
from __future__ import annotations

import json
from pathlib import Path

import typer
import yaml

from .discovery import discovery_progress, supported_workloads
from .engine import assess
from .models import AssessmentInput
from .report import render_html

app = typer.Typer(help="Grounded Fabric adoption readiness assessment")


@app.command("workloads")
def workloads_command() -> None:
    """List workload types accepted by the knowledge base."""
    typer.echo(json.dumps(supported_workloads(), indent=2))


@app.command("questions")
def questions_command(
    workload_type: str,
    answers_json: str = typer.Option("{}", help="Previously confirmed answers as JSON"),
) -> None:
    """Return the next conversational discovery questions."""
    answers = json.loads(answers_json)
    typer.echo(json.dumps(discovery_progress(workload_type, answers), indent=2))


@app.command("assess")
def assess_command(
    intake: Path,
    html_out: Path = typer.Option(Path("readiness-report.html")),
    json_out: Path = typer.Option(Path("readiness-report.json")),
) -> None:
    """Validate an intake and produce consistent JSON and HTML outputs."""
    raw = yaml.safe_load(intake.read_text(encoding="utf-8"))
    report = assess(AssessmentInput.model_validate(raw))
    json_out.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    html_out.write_text(render_html(report), encoding="utf-8")
    typer.echo(f"Wrote {json_out}")
    typer.echo(f"Wrote {html_out}")


if __name__ == "__main__":
    app()
