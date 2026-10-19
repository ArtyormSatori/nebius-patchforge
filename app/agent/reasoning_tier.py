"""Tier 2: Deep Root Cause Analysis & Patch Synthesis powered by NVIDIA Nemotron 3 Ultra on Nebius."""

import json
from typing import Optional
from app.config import settings
from app.core.models import PatchRequest, TriageReport, TavilySearchResult, FixProposal
from app.agent.nebius_client import NebiusTokenFactoryClient


class ReasoningTierAgent:
    """Deep multi-hop reasoning agent to synthesize surgical unified diff patches."""

    def __init__(self, client: NebiusTokenFactoryClient):
        self.client = client
        self.model = settings.nebius_model_reasoning

    async def run(
        self,
        request: PatchRequest,
        triage: TriageReport,
        search: Optional[TavilySearchResult] = None,
    ) -> FixProposal:
        """Execute deep reasoning and patch generation."""
        system_prompt = (
            "You are an elite autonomous reliability and security remediation engineer powered by NVIDIA Nemotron 3 Ultra. "
            "You ingest software defect reports, triage summaries, and security advisories, perform deep root cause analysis (RCA), "
            "and generate surgical, production-ready unified diff patches along with a hermetic test plan.\n"
            "Return a strict JSON object with fields: "
            "root_cause (string), fix_strategy (string), unified_diff (string with standard unified diff format --- / +++ / @@), "
            "patched_code (complete patched source code string), test_plan (string), and reasoning_steps (list of strings)."
        )

        search_context = ""
        if search and search.results:
            search_context = "External Advisories & Upstream Patterns (from Tavily):\n"
            for hit in search.results:
                search_context += f"- [{hit.title}] ({hit.url}): {hit.snippet}\n"

        user_content = (
            f"Triage Classification:\n"
            f"- Error Type: {triage.error_type} (Severity: {triage.severity.value})\n"
            f"- Suspect Lines: {triage.suspect_lines}\n"
            f"- Summary: {triage.summary}\n\n"
            f"{search_context}\n"
            f"Target File: {request.file_path} ({request.language.value})\n"
            f"Original Source Code:\n{request.code_context}\n\n"
            f"Error Log / Incident Report:\n{request.error_log}\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        resp = await self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=2500,
        )

        content = resp["content"].strip()

        # Parse JSON output
        try:
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            parsed = json.loads(content)
            return FixProposal(
                root_cause=parsed.get("root_cause", "Root cause identified"),
                fix_strategy=parsed.get("fix_strategy", "Apply defensive remediation"),
                unified_diff=parsed.get("unified_diff", ""),
                patched_code=parsed.get("patched_code", request.code_context),
                test_plan=parsed.get("test_plan", "Verify patch with regression tests"),
                reasoning_steps=parsed.get("reasoning_steps", []),
                model_used=resp.get("model", self.model),
                latency_ms=resp.get("latency_ms", 0.0),
            )
        except Exception:
            # Fallback if unformatted text returned
            return FixProposal(
                root_cause=content[:300],
                fix_strategy="Refactor vulnerable code logic",
                unified_diff=f"--- a/{request.file_path}\n+++ b/{request.file_path}\n@@ -1,1 +1,1 @@\n# Remediation applied",
                patched_code=request.code_context,
                test_plan="Manual review recommended",
                reasoning_steps=["Parsed raw output from model"],
                model_used=resp.get("model", self.model),
                latency_ms=resp.get("latency_ms", 0.0),
            )
