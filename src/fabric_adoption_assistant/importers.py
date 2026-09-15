"""Review-first importers for customer estate documents."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .knowledge_base import load_knowledge_base
from .models import AssessmentInput, WorkloadInput


class ImportIssue(BaseModel):
    location: str
    message: str


class ExtractedPage(BaseModel):
    page_number: int = Field(ge=1)
    text: str


class EstateImport(BaseModel):
    source_file: str
    source_type: str
    customer_name: str
    workloads: list[WorkloadInput] = Field(default_factory=list)
    extracted_pages: list[ExtractedPage] = Field(default_factory=list)
    issues: list[ImportIssue] = Field(default_factory=list)
    requires_confirmation: bool = True

    def to_assessment_input(self) -> AssessmentInput:
        return AssessmentInput(customer_name=self.customer_name, workloads=self.workloads)


_TYPE_ALIASES = {
    "power bi": "power_bi",
    "powerbi": "power_bi",
    "ssas": "ssas_aas",
    "azure analysis services": "ssas_aas",
    "aas": "ssas_aas",
    "azure sql": "azure_sql",
    "synapse": "synapse",
    "azure synapse": "synapse",
    "databricks": "databricks",
    "azure databricks": "databricks",
    "adf": "adf",
    "azure data factory": "adf",
    "logic apps": "logic_apps",
    "azure logic apps": "logic_apps",
    "spark": "spark_jobs",
    "spark jobs": "spark_jobs",
    "automation runbooks": "automation_runbooks",
    "azure automation": "automation_runbooks",
}


def normalize_workload_type(value: str) -> str | None:
    normalized = value.strip().lower().replace("-", " ").replace("_", " ")
    alias = _TYPE_ALIASES.get(normalized)
    if alias:
        return alias
    canonical = value.strip().lower()
    return canonical if canonical in load_knowledge_base() else None


def _optional_float(value: str | None, location: str, issues: list[ImportIssue]) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        parsed = float(value)
    except ValueError:
        issues.append(ImportIssue(location=location, message=f"Invalid size_gb value: {value!r}"))
        return None
    if parsed < 0:
        issues.append(ImportIssue(location=location, message="size_gb cannot be negative"))
        return None
    return parsed


def import_csv(path: Path, customer_name: str) -> EstateImport:
    """Import explicit inventory columns; never derive assessment answers."""
    issues: list[ImportIssue] = []
    workloads: list[WorkloadInput] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = {header.strip().lower() for header in (reader.fieldnames or []) if header}
        missing = {"name", "workload_type"} - headers
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"CSV is missing required columns: {names}")

        for row_number, raw_row in enumerate(reader, start=2):
            row: dict[str, Any] = {
                str(key).strip().lower(): value for key, value in raw_row.items() if key is not None
            }
            name = str(row.get("name") or "").strip()
            raw_type = str(row.get("workload_type") or "").strip()
            location = f"row {row_number}"
            if not name:
                issues.append(ImportIssue(location=location, message="Missing workload name; row skipped"))
                continue
            workload_type = normalize_workload_type(raw_type)
            if not workload_type:
                issues.append(
                    ImportIssue(
                        location=location,
                        message=f"Unsupported workload_type {raw_type!r}; row skipped",
                    )
                )
                continue
            workloads.append(
                WorkloadInput(
                    name=name,
                    workload_type=workload_type,
                    size_gb=_optional_float(row.get("size_gb"), location, issues),
                    notes=str(row.get("notes") or "").strip() or None,
                    source_reference=f"{path.name}, row {row_number}",
                    answers={},
                )
            )

    return EstateImport(
        source_file=path.name,
        source_type="csv",
        customer_name=customer_name,
        workloads=workloads,
        issues=issues,
    )


def import_pdf(path: Path, customer_name: str) -> EstateImport:
    """Extract PDF text for conversation; never classify workloads automatically."""
    from pypdf import PdfReader

    reader = PdfReader(path)
    pages: list[ExtractedPage] = []
    issues: list[ImportIssue] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(ExtractedPage(page_number=page_number, text=text))
        else:
            issues.append(
                ImportIssue(
                    location=f"page {page_number}",
                    message="No text extracted; the page may be scanned and require OCR",
                )
            )
    return EstateImport(
        source_file=path.name,
        source_type="pdf",
        customer_name=customer_name,
        extracted_pages=pages,
        issues=issues,
    )


def import_estate(path: Path, customer_name: str) -> EstateImport:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return import_csv(path, customer_name)
    if suffix == ".pdf":
        return import_pdf(path, customer_name)
    raise ValueError("Only .csv and .pdf estate files are supported")
