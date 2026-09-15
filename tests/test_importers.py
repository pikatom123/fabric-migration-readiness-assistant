from pathlib import Path

import pytest

from fabric_adoption_assistant.engine import assess
from fabric_adoption_assistant.importers import import_csv, import_pdf, normalize_workload_type
from fabric_adoption_assistant.models import Disposition


def test_csv_import_creates_unanswered_drafts(tmp_path: Path):
    source = tmp_path / "estate.csv"
    source.write_text(
        "name,workload_type,size_gb,notes\nSales model,Power BI,12,Important model\n",
        encoding="utf-8",
    )

    imported = import_csv(source, "Contoso")
    report = assess(imported.to_assessment_input())

    assert len(imported.workloads) == 1
    assert imported.workloads[0].answers == {}
    assert imported.workloads[0].source_reference == "estate.csv, row 2"
    assert report.assessments[0].disposition == Disposition.NEEDS_DISCOVERY


def test_csv_skips_unknown_type_and_records_issue(tmp_path: Path):
    source = tmp_path / "estate.csv"
    source.write_text("name,workload_type\nMystery,Unknown Product\n", encoding="utf-8")

    imported = import_csv(source, "Contoso")

    assert not imported.workloads
    assert "Unsupported workload_type" in imported.issues[0].message


def test_csv_requires_name_and_workload_type_headers(tmp_path: Path):
    source = tmp_path / "estate.csv"
    source.write_text("asset,technology\nModel,Power BI\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        import_csv(source, "Contoso")


def test_known_type_aliases_are_normalized():
    assert normalize_workload_type("Azure Data Factory") == "adf"
    assert normalize_workload_type("power_bi") == "power_bi"


def test_blank_pdf_page_requires_ocr_and_infers_no_workloads(tmp_path: Path):
    pypdf = pytest.importorskip("pypdf")
    source = tmp_path / "scanned.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as handle:
        writer.write(handle)

    imported = import_pdf(source, "Contoso")

    assert not imported.workloads
    assert not imported.extracted_pages
    assert "require OCR" in imported.issues[0].message
