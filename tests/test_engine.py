from datetime import date

import pytest

from fabric_adoption_assistant.engine import assess_workload
from fabric_adoption_assistant.models import Disposition, EvidenceSource, WorkloadInput


def test_missing_required_answers_never_claims_readiness():
    result = assess_workload(WorkloadInput(name="Unknown model", workload_type="power_bi"))

    assert result.disposition == Disposition.NEEDS_DISCOVERY
    assert result.confidence_percent == 0
    assert result.unanswered_questions


def test_explicit_blocker_wins_even_when_discovery_is_incomplete():
    result = assess_workload(
        WorkloadInput(
            name="Legacy cube",
            workload_type="ssas_aas",
            answers={"model_type": "multidimensional"},
        )
    )

    assert result.disposition == Disposition.BLOCKED
    assert result.blockers


def test_complete_grounded_workload_can_be_as_is():
    evidence = EvidenceSource(
        title="Microsoft Learn validation",
        url="https://learn.microsoft.com/fabric/",
        claim="Target pattern checked against current product documentation.",
        retrieved_on=date(2026, 9, 15),
    )
    result = assess_workload(
        WorkloadInput(
            name="Import model",
            workload_type="power_bi",
            answers={
                "storage_mode": "import",
                "calculated_objects": False,
                "gateway_required": False,
                "peak_concurrent_users": 25,
            },
            evidence=[evidence],
        )
    )

    assert result.disposition == Disposition.AS_IS
    assert result.confidence_percent == 100
    assert not result.limitations


def test_false_answer_is_not_treated_as_missing():
    result = assess_workload(
        WorkloadInput(
            name="ADF pipelines",
            workload_type="adf",
            answers={
                "uses_shir": False,
                "uses_ssis": False,
                "connector_inventory_complete": True,
            },
        )
    )

    assert result.disposition == Disposition.AS_IS
    assert result.confidence_percent == 100


def test_confirmed_incomplete_inventory_explains_needs_discovery():
    result = assess_workload(
        WorkloadInput(
            name="ADF pipelines",
            workload_type="adf",
            answers={
                "uses_shir": False,
                "uses_ssis": False,
                "connector_inventory_complete": False,
            },
        )
    )

    assert result.disposition == Disposition.NEEDS_DISCOVERY
    assert result.confidence_percent == 100
    assert any("unfinished discovery work" in item for item in result.limitations)


def test_unknown_answer_id_fails_instead_of_becoming_an_assumption():
    workload = WorkloadInput(
        name="Model",
        workload_type="power_bi",
        answers={"storage_mod": "import"},
    )

    with pytest.raises(ValueError, match="Unknown answer ids"):
        assess_workload(workload)


def test_invalid_choice_fails_instead_of_using_base_disposition():
    workload = WorkloadInput(
        name="Model",
        workload_type="power_bi",
        answers={"storage_mode": "sometimes"},
    )

    with pytest.raises(ValueError, match="Invalid value"):
        assess_workload(workload)
