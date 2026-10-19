"""Data models and schemas for PatchForge-Nemotron."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    GENERIC = "generic"


class PatchRequest(BaseModel):
    """Input payload to trigger autonomous patch generation."""
    title: str = Field(..., description="Short title or ticket identifier (e.g., CVE-2024-XXXX, KeyError in auth handler)")
    error_log: str = Field(..., description="Stack trace, crash log, or vulnerability finding")
    code_context: str = Field(..., description="Target source code to be inspected and patched")
    file_path: str = Field(default="app/handler.py", description="Relative path of the target file")
    language: Language = Field(default=Language.PYTHON, description="Programming language")
    enable_tavily_search: bool = Field(default=True, description="Query Tavily for live CVE intelligence & fixes")


class TriageReport(BaseModel):
    """Output of Tier 1 fast triage (NVIDIA Nemotron Nano)."""
    error_type: str = Field(..., description="Classified error type (e.g. SQLInjection, UnhandledException)")
    summary: str = Field(..., description="Fast triage summary")
    severity: SeverityLevel = Field(default=SeverityLevel.HIGH, description="Estimated severity")
    suspect_lines: List[int] = Field(default_factory=list, description="Candidate line numbers identified")
    syntax_valid: bool = Field(default=True, description="Whether original code passes syntax parsing")
    confidence_score: float = Field(default=0.95, description="Confidence score from triage model")
    model_used: str = Field(..., description="Model identifier used for Tier 1 triage")
    latency_ms: float = Field(default=0.0, description="Latency in milliseconds")


class SearchHit(BaseModel):
    title: str
    url: str
    snippet: str


class TavilySearchResult(BaseModel):
    """External context fetched via Tavily API."""
    query: str
    results: List[SearchHit] = Field(default_factory=list)
    live_call: bool = Field(default=False)
    summary: str = Field(default="")


class FixProposal(BaseModel):
    """Output of Tier 2 deep reasoning (NVIDIA Nemotron 3 Ultra)."""
    root_cause: str = Field(..., description="Deep root-cause analysis")
    fix_strategy: str = Field(..., description="Architectural strategy to remedy root cause")
    unified_diff: str = Field(..., description="Surgical Unified Diff patch (--- / +++)")
    patched_code: str = Field(..., description="Complete patched source code")
    test_plan: str = Field(..., description="Hermetic test verification instructions")
    reasoning_steps: List[str] = Field(default_factory=list, description="Step-by-step reasoning trace")
    model_used: str = Field(..., description="Model identifier used for Tier 2 deep reasoning")
    latency_ms: float = Field(default=0.0, description="Latency in milliseconds")


class PatchVerification(BaseModel):
    """Hermetic validation of generated diff and patched code."""
    applied_cleanly: bool = Field(..., description="Whether diff applies cleanly to original code")
    syntax_ok: bool = Field(..., description="Whether patched code passes AST syntax check")
    lint_messages: List[str] = Field(default_factory=list, description="Lint messages or warnings")
    tests_passed: bool = Field(default=True, description="Whether automated sanity checks pass")
    details: str = Field(default="", description="Diagnostic details")


class PatchJobResult(BaseModel):
    """Complete lifecycle result for an autonomous patching job."""
    job_id: str
    status: str = Field(default="COMPLETED")
    created_at: str
    completed_at: Optional[str] = None
    request: PatchRequest
    triage: Optional[TriageReport] = None
    search: Optional[TavilySearchResult] = None
    proposal: Optional[FixProposal] = None
    verification: Optional[PatchVerification] = None
    error_message: Optional[str] = None
