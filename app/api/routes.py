"""FastAPI API routes for PatchForge-Nemotron."""

from typing import List, Dict
from fastapi import APIRouter, HTTPException
from app.config import settings
from app.core.models import PatchRequest, PatchJobResult
from app.core.presets import PRESET_SCENARIOS
from app.agent.pipeline import PatchForgePipeline

router = APIRouter(prefix="/api", tags=["PatchForge"])

# In-memory store of recent jobs
_JOBS_STORE: Dict[str, PatchJobResult] = {}
_pipeline = PatchForgePipeline()


@router.get("/health")
async def health_check():
    """Return system health and model connectivity status."""
    return {
        "status": "healthy",
        "service": "PatchForge-Nemotron",
        "nebius": {
            "api_base": settings.nebius_api_base,
            "is_live": settings.is_nebius_live,
            "mode": "Live Nebius Token Factory" if settings.is_nebius_live else "Simulation Mock (Awaiting User API Key)",
            "models": {
                "fast_tier": settings.nebius_model_fast,
                "reasoning_tier": settings.nebius_model_reasoning,
            },
        },
        "tavily": {
            "is_live": settings.is_tavily_live,
            "mode": "Live Tavily API" if settings.is_tavily_live else "Simulation Mock (Awaiting User API Key)",
        },
    }


@router.get("/presets")
async def get_presets():
    """Return preset real-world defect and vulnerability scenarios."""
    return PRESET_SCENARIOS


@router.post("/patch/analyze", response_model=PatchJobResult)
async def analyze_and_patch(request: PatchRequest):
    """Trigger autonomous remediation pipeline for given defect report."""
    result = await _pipeline.execute(request)
    _JOBS_STORE[result.job_id] = result
    return result


@router.get("/patch/jobs", response_model=List[PatchJobResult])
async def list_jobs():
    """List all recently processed patch jobs."""
    return list(_JOBS_STORE.values())


@router.get("/patch/job/{job_id}", response_model=PatchJobResult)
async def get_job(job_id: str):
    """Retrieve details of a specific patch job by ID."""
    if job_id not in _JOBS_STORE:
        raise HTTPException(status_code=404, detail="Job not found")
    return _JOBS_STORE[job_id]
