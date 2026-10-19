# PatchForge-Nemotron: Autonomous Reliability & Security Patching Agent

> **Built for the Nebius x NVIDIA Global AI Hackathon (Devpost)**  
> **Track:** Coding and Agentic Engineering Track  
> **Bonus Category:** Best Use of Tavily

---

## 🚀 Overview

**PatchForge-Nemotron** is an end-to-end autonomous software reliability and vulnerability remediation agent designed for developer platforms, CI/CD pipelines, and SRE operations. It ingests software issues, stack traces, and CVE security alerts, synthesizes root causes, searches upstream fixes and security advisories via Tavily, and generates verified, hermetic diff patches.

### 🧠 Dual-Tier NVIDIA Nemotron Intelligence on Nebius
To maximize performance, reasoning depth, and cost efficiency, PatchForge adopts a hierarchical two-tier model architecture served through **Nebius Token Factory**:
1. **Tier 1 (Fast Triage & Syntax Guard):** Powered by **NVIDIA Nemotron Nano / Super**, handling sub-second log ingestion, AST error extraction, and lint validation.
2. **Tier 2 (Deep Root Cause Analysis & Patch Synthesis):** Powered by **NVIDIA Nemotron 3 Ultra** (or Llama-3.1-Nemotron-70B), performing multi-hop reasoning across callgraphs, vulnerability surface modeling, and generating surgical code diffs.
3. **External Context & Advisory Search:** Powered by **Tavily Search API**, fetching live CVE documentation, library migration diffs, and security advisories at runtime.

---

## 🛠️ Architecture

```
Issue / Stacktrace / CVE
          │
          ▼
┌─────────────────────────┐
│   Fast Ingest & Triage  │  ◄── NVIDIA Nemotron Nano (Nebius Token Factory)
└───────────┬─────────────┘
            │
            ├──────────────► [Tavily Search API] (CVE Intelligence & Advisory Fetch)
            ▼
┌─────────────────────────┐
│  Deep Root Cause & Fix  │  ◄── NVIDIA Nemotron 3 Ultra (Nebius Token Factory)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Sandboxed Verification  │  ◄── Unit Tests / Syntax Validation / Diff Checking
└───────────┬─────────────┘
            │
            ▼
Verified Unified Patch & PR Artifact + Visual DAG Execution Trace
```

---

## 📦 Quickstart

### Prerequisites
- Python 3.11+
- Nebius Token Factory API Key (`NEBIUS_API_KEY`)
- Tavily API Key (`TAVILY_API_KEY`)

### Setup
```bash
git clone https://github.com/<your-username>/nebius-patchforge.git
cd nebius-patchforge
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
python -m app.main
```

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
