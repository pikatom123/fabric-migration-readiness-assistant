from fabric_adoption_assistant.engine import assess
from fabric_adoption_assistant.models import AssessmentInput, WorkloadInput
from fabric_adoption_assistant.report import render_html


def test_html_report_contains_grounding_and_unknowns():
    report = assess(
        AssessmentInput(
            customer_name="Contoso",
            workloads=[WorkloadInput(name="Unknown ADF", workload_type="adf")],
        )
    )

    html = render_html(report)

    assert "Fabric adoption readiness" in html
    assert "Needs Discovery" in html
    assert "No Microsoft Learn evidence snapshot is attached" in html
    assert "Unknown ADF" in html


def test_html_report_escapes_customer_content():
    report = assess(
        AssessmentInput(
            customer_name="<script>alert('customer')</script>",
            engagement_owner="<img src=x onerror=alert('owner')>",
            workloads=[WorkloadInput(name="<b>unsafe</b>", workload_type="adf")],
        )
    )

    html = render_html(report)

    assert "<script>alert" not in html
    assert "<img src=x" not in html
    assert "<b>unsafe</b>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;unsafe&lt;/b&gt;" in html
