"""End-to-End Orchestrator connecting Nemotron Dual-Tier inference, Tavily search, and verification."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable
from app.core.models import (
    PatchRequest,
    PatchJobResult,
    TriageReport,
    TavilySearchResult,
    FixProposal,
    PatchVerification,
)
from app.core.verifier import PatchVerifier
from app.agent.nebius_client import NebiusTokenFactoryClient
from app.agent.tavily_client import TavilySearchClient
from app.agent.triage_tier import TriageTierAgent
from app.agent.reasoning_tier import ReasoningTierAgent


class PatchForgePipeline:
    """Coordinates autonomous analysis, intelligence search, patch synthesis, and verification."""

    def __init__(
        self,
        nebius_client: Optional[NebiusTokenFactoryClient] = None,
        tavily_client: Optional[TavilySearchClient] = None,
    ):
        self.nebius_client = nebius_client or NebiusTokenFactoryClient()
        self.tavily_client = tavily_client or TavilySearchClient()
        self.triage_agent = TriageTierAgent(self.nebius_client)
        self.reasoning_agent = ReasoningTierAgent(self.nebius_client)

    async def execute(
        self,
        request: PatchRequest,
        event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> PatchJobResult:
        """Execute complete autonomous remediation pipeline."""
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        def emit(event: str, data: Dict[str, Any]):
            if event_callback:
                event_callback(event, data)

        emit("job_started", {"job_id": job_id, "title": request.title})

        try:
            # 1. Tier 1: Fast Triage & Syntax Guard
            emit("triage_started", {"model": self.triage_agent.model})
            triage_report = await self.triage_agent.run(request)
            emit("triage_completed", triage_report.model_dump())

            # 2. Intelligence Search via Tavily
            search_result: Optional[TavilySearchResult] = None
            if request.enable_tavily_search:
                query = f"{triage_report.error_type} {request.language.value} fix advisory"
                emit("search_started", {"query": query})
                search_result = await self.tavily_client.search(query)
                emit("search_completed", search_result.model_dump())

            # 3. Tier 2: Deep RCA & Patch Synthesis
            emit("reasoning_started", {"model": self.reasoning_agent.model})
            proposal = await self.reasoning_agent.run(request, triage_report, search_result)
            emit("reasoning_completed", proposal.model_dump())

            # 4. Hermetic Verification
            emit("verification_started", {})
            verification = PatchVerifier.verify(
                original_code=request.code_context,
                patched_code=proposal.patched_code,
                unified_diff=proposal.unified_diff,
                language=request.language,
            )
            emit("verification_completed", verification.model_dump())

            completed_iso = datetime.now(timezone.utc).isoformat()
            result = PatchJobResult(
                job_id=job_id,
                status="COMPLETED" if verification.tests_passed else "VERIFICATION_FAILED",
                created_at=now_iso,
                completed_at=completed_iso,
                request=request,
                triage=triage_report,
                search=search_result,
                proposal=proposal,
                verification=verification,
            )
            emit("job_finished", result.model_dump())
            return result

        except Exception as e:
            completed_iso = datetime.now(timezone.utc).isoformat()
            result = PatchJobResult(
                job_id=job_id,
                status="FAILED",
                created_at=now_iso,
                completed_at=completed_iso,
                request=request,
                error_message=str(e),
            )
            emit("job_failed", {"error": str(e)})
            return result
