"""Tier 1: Fast Triage & Syntax Guard powered by NVIDIA Nemotron Nano on Nebius."""

import json
from app.config import settings
from app.core.models import PatchRequest, TriageReport, SeverityLevel
from app.core.verifier import PatchVerifier
from app.agent.nebius_client import NebiusTokenFactoryClient


class TriageTierAgent:
    """Sub-second triage agent to classify errors and localize suspect lines."""

    def __init__(self, client: NebiusTokenFactoryClient):
        self.client = client
        self.model = settings.nebius_model_fast

    async def run(self, request: PatchRequest) -> TriageReport:
        """Execute fast triage analysis."""
        # 1. Pre-flight check: syntax check on original code
        syntax_valid, _ = PatchVerifier.verify_syntax(request.code_context, request.language)

        # 2. Prompt Nemotron Nano
        system_prompt = (
            "You are a sub-second software triage agent running on NVIDIA Nemotron Nano. "
            "Your task is to analyze the error log, stacktrace, or vulnerability finding, "
            "localize suspect lines, classify error category, and return a strict JSON object with: "
            "error_type (string), summary (string), severity ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'), "
            "suspect_lines (list of integers), syntax_valid (boolean), and confidence_score (float)."
        )

        user_content = (
            f"Title: {request.title}\n"
            f"File: {request.file_path} ({request.language.value})\n"
            f"Error Log:\n{request.error_log}\n\n"
            f"Source Code:\n{request.code_context}\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        resp = await self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=512,
        )

        content = resp["content"].strip()

        # Parse JSON
        try:
            # Strip markdown json codeblocks if any
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            parsed = json.loads(content)
            severity = SeverityLevel(parsed.get("severity", "HIGH"))
            return TriageReport(
                error_type=parsed.get("error_type", "GeneralBug"),
                summary=parsed.get("summary", "Triage completed"),
                severity=severity,
                suspect_lines=parsed.get("suspect_lines", []),
                syntax_valid=syntax_valid,
                confidence_score=float(parsed.get("confidence_score", 0.95)),
                model_used=resp.get("model", self.model),
                latency_ms=resp.get("latency_ms", 0.0),
            )
        except Exception:
            # Fallback if raw text returned
            return TriageReport(
                error_type="ClassifiedException",
                summary=content[:200],
                severity=SeverityLevel.HIGH,
                suspect_lines=[1],
                syntax_valid=syntax_valid,
                confidence_score=0.90,
                model_used=resp.get("model", self.model),
                latency_ms=resp.get("latency_ms", 0.0),
            )
