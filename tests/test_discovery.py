from fabric_adoption_assistant.discovery import discovery_progress, next_questions, supported_workloads


def test_discovery_asks_only_unanswered_questions_in_small_batches():
    questions = next_questions("power_bi", {"storage_mode": "import"}, limit=2)

    assert len(questions) == 2
    assert all(question.id != "storage_mode" for question in questions)


def test_progress_exposes_docs_query_for_mcp_grounding():
    progress = discovery_progress("adf", {})

    assert progress["docs_query"]
    assert not progress["complete"]


def test_supported_workloads_come_from_knowledge_base():
    workload_ids = {item["id"] for item in supported_workloads()}

    assert {"power_bi", "adf", "databricks"}.issubset(workload_ids)
