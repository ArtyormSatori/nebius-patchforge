"""Tests for FastAPI endpoints."""

from starlette.testclient import TestClient
from app.main import app
from app.core.presets import PRESET_SCENARIOS

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "PatchForge" in response.text
    assert "Nemotron" in response.text


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "nebius" in data
    assert "tavily" in data
    assert "nvidia/nemotron" in data["nebius"]["models"]["fast_tier"].lower()


def test_presets_endpoint():
    response = client.get("/api/presets")
    assert response.status_code == 200
    presets = response.json()
    assert isinstance(presets, list)
    assert len(presets) >= 3
    assert any(p["id"] == "cwe-89-sqli" for p in presets)


def test_analyze_and_patch_endpoint():
    preset = PRESET_SCENARIOS[0]
    payload = {
        "title": preset["title"],
        "error_log": preset["error_log"],
        "code_context": preset["code_context"],
        "file_path": preset["file_path"],
        "language": preset["language"],
        "enable_tavily_search": True,
    }

    response = client.post("/api/patch/analyze", json=payload)
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "COMPLETED"
    assert "job_id" in job
    assert job["proposal"] is not None
    assert "unified_diff" in job["proposal"]

    # Verify listing and single get
    job_id = job["job_id"]
    get_res = client.get(f"/api/patch/job/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["job_id"] == job_id

    list_res = client.get("/api/patch/jobs")
    assert list_res.status_code == 200
    jobs = list_res.json()
    assert any(j["job_id"] == job_id for j in jobs)
