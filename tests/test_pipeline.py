"""End-to-end tests for PatchForgePipeline."""

import asyncio
from app.core.models import PatchRequest, Language
from app.core.presets import PRESET_SCENARIOS
from app.agent.pipeline import PatchForgePipeline


def test_pipeline_sqli_scenario():
    preset = PRESET_SCENARIOS[0]  # SQLi
    request = PatchRequest(
        title=preset["title"],
        error_log=preset["error_log"],
        code_context=preset["code_context"],
        file_path=preset["file_path"],
        language=Language(preset["language"]),
        enable_tavily_search=True,
    )

    events = []
    def on_event(ev, data):
        events.append(ev)

    pipeline = PatchForgePipeline()
    result = asyncio.run(pipeline.execute(request, event_callback=on_event))

    assert result.status == "COMPLETED"
    assert result.job_id.startswith("job-")
    assert result.triage is not None
    assert result.triage.error_type == "SQLInjection"
    assert result.search is not None
    assert result.proposal is not None
    assert "SELECT" in result.proposal.patched_code
    assert result.verification is not None
    assert result.verification.tests_passed is True
    assert "additions" in result.verification.diff_stats

    # Check that events fired in order
    assert "job_started" in events
    assert "triage_started" in events
    assert "triage_completed" in events
    assert "search_started" in events
    assert "reasoning_completed" in events
    assert "verification_completed" in events
    assert "job_finished" in events


def test_pipeline_path_traversal_scenario():
    preset = PRESET_SCENARIOS[1]  # Path traversal
    request = PatchRequest(
        title=preset["title"],
        error_log=preset["error_log"],
        code_context=preset["code_context"],
        file_path=preset["file_path"],
        language=Language(preset["language"]),
        enable_tavily_search=True,
    )

    pipeline = PatchForgePipeline()
    result = asyncio.run(pipeline.execute(request))

    assert result.status == "COMPLETED"
    assert result.triage is not None
    assert result.triage.error_type == "PathTraversal"
    assert result.proposal is not None
    assert "realpath" in result.proposal.patched_code or "safe_path" in result.proposal.patched_code
    assert result.verification is not None
    assert result.verification.tests_passed is True


def test_pipeline_ssrf_scenario():
    preset = [p for p in PRESET_SCENARIOS if p["id"] == "cwe-918-ssrf"][0]
    request = PatchRequest(
        title=preset["title"],
        error_log=preset["error_log"],
        code_context=preset["code_context"],
        file_path=preset["file_path"],
        language=Language(preset["language"]),
        enable_tavily_search=True,
    )

    pipeline = PatchForgePipeline()
    result = asyncio.run(pipeline.execute(request))

    assert result.status == "COMPLETED"
    assert result.triage is not None
    assert result.triage.error_type == "ServerSideRequestForgery"
    assert result.proposal is not None
    assert "is_safe_webhook_url" in result.proposal.patched_code
    assert result.verification is not None
    assert result.verification.tests_passed is True


def test_pipeline_deserialization_scenario():
    preset = [p for p in PRESET_SCENARIOS if p["id"] == "cwe-502-insecure-deserialization"][0]
    request = PatchRequest(
        title=preset["title"],
        error_log=preset["error_log"],
        code_context=preset["code_context"],
        file_path=preset["file_path"],
        language=Language(preset["language"]),
        enable_tavily_search=True,
    )

    pipeline = PatchForgePipeline()
    result = asyncio.run(pipeline.execute(request))

    assert result.status == "COMPLETED"
    assert result.triage is not None
    assert result.triage.error_type == "InsecureDeserialization"
    assert result.proposal is not None
    assert "json.loads" in result.proposal.patched_code
    assert result.verification is not None
    assert result.verification.tests_passed is True
