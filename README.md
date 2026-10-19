# PatchForge-Nemotron: Autonomous Reliability & Security Patching Agent

> **Built for the Nebius x NVIDIA Global AI Hackathon (Devpost)**  
> **Track:** Coding and Agentic Engineering Track  
> **Bonus Category:** Best Use of Tavily

[![CI Tests](https://img.shields.io/badge/pytest-19%20passed-emerald?style=flat-square&logo=pytest)](https://github.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Nebius Token Factory](https://img.shields.io/badge/Nebius-Nemotron%20Inference-7c3aed?style=flat-square)](https://nebius.com)
[![NVIDIA Nemotron](https://img.shields.io/badge/NVIDIA-Nemotron%20Models-76b900?style=flat-square&logo=nvidia)](https://developer.nvidia.com/nemotron)
[![Tavily Search](https://img.shields.io/badge/Tavily-Security%20Search%20API-blue?style=flat-square)](https://tavily.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🚀 Overview

**PatchForge-Nemotron** is an autonomous security remediation and software reliability agent. It ingests software vulnerability alerts, stack traces, and defect reports, performs multi-tier root cause analysis, queries upstream CVE and security advisories via the **Tavily Search API**, and synthesizes surgical, verified unified diff patches validated through a hermetic syntax and AST engine.

### Why Dual-Tier Nemotron on Nebius?
Large monolithic reasoning models are often too slow and costly for initial log ingestion and syntax validation, while small models lack the multi-hop reasoning required to resolve subtle vulnerabilities like race conditions, SSRF, or insecure deserialization.

PatchForge solves this by adopting a **two-tier hierarchical agent architecture** powered by **NVIDIA Nemotron models hosted on Nebius Token Factory**:

1. **Fast Triage & Syntax Guard Tier (NVIDIA Nemotron Nano / Mini):**
   - Sub-second ingestion of raw logs and code contexts.
   - AST-guided error classification, CWE taxonomy tagging, and suspect line localization.
2. **Deep Reasoning & Remediation Tier (NVIDIA Nemotron 70B / 49B / 340B Ultra):**
   - Multi-hop causal reasoning over control flow and callgraphs.
   - Incorporation of live Tavily CVE threat advisories.
   - Surgical unified diff patch synthesis without regressions or unnecessary churn.
3. **External Context & Advisory Search (Tavily Search API):**
   - Real-time retrieval of official OWASP remediation cheat sheets, CVE databases, and advisory benchmarks.
4. **Hermetic Verification Engine:**
   - Pre-patch and post-patch Python AST syntax validation.
   - Unified diff chunk validation (`diff_stats` measuring additions, deletions, net line delta).
   - Test plan extraction and assertion consistency checking.

---

## 🛠️ Architecture & Pipeline DAG

```
   Raw Error Log / Stacktrace / Vulnerability Report
                           │
                           ▼
   ┌────────────────────────────────────────────────────────┐
   │  Step 1: FAST TRIAGE & CLASSIFICATION                   │
   │  Model: NVIDIA Nemotron-Mini-4B (Nebius Token Factory) │
   │  - Parses stacktraces & extracts defect taxonomy       │
   │  - Pinpoints suspect code lines (CWE classification)   │
   └───────────────────────┬────────────────────────────────┘
                           │
                           ├────────────────────────────────┐
                           ▼                                ▼
   ┌──────────────────────────────────────┐     ┌───────────────────────┐
   │  Step 2: LIVE ADVISORY SEARCH        │     │  Context Aggregator   │
   │  Engine: Tavily Search API           │────►│  Combines Code + CWE  │
   │  - Live OWASP prevention patterns    │     │  Advisories + Query   │
   │  - Upstream CVE remediation context  │     └───────────┬───────────┘
   └──────────────────────────────────────┘                 │
                                                            ▼
   ┌────────────────────────────────────────────────────────┐
   │  Step 3: DEEP REASONING & PATCH SYNTHESIS              │
   │  Model: NVIDIA Nemotron-4-340B / 70B (Nebius Factory)  │
   │  - Multi-hop root cause analysis (RCA)                 │
   │  - Generates surgical unified diff + full patched code │
   │  - Formulates verification test plan                   │
   └───────────────────────┬────────────────────────────────┘
                           │
                           ▼
   ┌────────────────────────────────────────────────────────┐
   │  Step 4: HERMETIC VERIFICATION & AUDIT                 │
   │  Engine: PatchForge Local Verifier                     │
   │  - Python AST syntax trees validation                  │
   │  - Unified diff format & line boundary verification    │
   │  - Generates diff_stats (+lines / -lines / net_lines)  │
   └───────────────────────┬────────────────────────────────┘
                           │
                           ▼
   ┌────────────────────────────────────────────────────────┐
   │  OUTPUT ARTIFACTS                                      │
   │  ✔ Interactive Real-time SSE Execution Trace           │
   │  ✔ Downloadable .patch file (text/x-diff)              │
   │  ✔ Automated remediation report with Root Cause & Plan │
   └────────────────────────────────────────────────────────┘
```

---

## 🔬 Pre-configured Security Presets

PatchForge comes out-of-the-box with **5 production-grade vulnerability presets** spanning the OWASP Top 10:

| ID | Vulnerability | CWE | Severity | Attack Surface & Remediation |
|---|---|---|---|---|
| `cwe-89-sqli` | SQL Injection | CWE-89 | **CRITICAL** | Raw string formatting in auth query -> Parameterized SQLAlchemy / DB-API bind parameters. |
| `cwe-22-path-traversal` | Path Traversal | CWE-22 | **HIGH** | Unchecked filename in file export -> `os.path.realpath` boundary jail containment. |
| `cwe-362-race-condition` | Concurrency Race Condition | CWE-362 | **HIGH** | Non-atomic check-then-act balance transfer -> `asyncio.Lock` critical section synchronization. |
| `cwe-918-ssrf` | Server-Side Request Forgery | CWE-918 | **CRITICAL** | Direct `urllib.request` on user webhook -> DNS check against private/loopback/cloud metadata IPs (RFC 1918, 169.254.169.254). |
| `cwe-502-insecure-deserialization` | Insecure Deserialization | CWE-502 | **CRITICAL** | Arbitrary object instantiation via `pickle.loads` -> Safe JSON token deserialization. |

---

## ⚡ Zero-Friction Evaluation (Dual Operation Mode)

PatchForge-Nemotron supports **two transparent operating modes**:

1. **Live Nebius & Tavily Cloud Mode:**
   - Point your `NEBIUS_API_KEY` and `TAVILY_API_KEY` in `.env`.
   - All prompts are dispatched live to Nebius Token Factory endpoints using `nvidia/nemotron-mini-4b-instruct` and `nvidia/nemotron-4-340b-instruct`.
2. **Hermetic Simulation Mode (Offline / Zero-Credentials):**
   - When no API keys are provided, PatchForge automatically engages its internal hermetic token simulator.
   - Hackathon judges and peer reviewers can clone and evaluate the **full end-to-end agent workflow, UI, SSE streams, verification passes, and .patch exports without needing to register accounts or incur cloud costs**.

---

## 📦 Quickstart (Local Run)

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/ArtyormSatori/nebius-patchforge.git
cd nebius-patchforge

# Create and activate virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables (Optional)
```bash
cp .env.example .env
# Edit .env with your keys if running in live mode:
# NEBIUS_API_KEY=your_nebius_api_key_here
# TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Run Application
```bash
# Using the startup script
./run_local.sh

# Or directly via uvicorn
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at **`http://localhost:8000`** to access the interactive web console.

---

## 🧪 Running the Test Suite

PatchForge includes a comprehensive automated test suite (19 tests) validating API routes, SSE streaming, multi-tier agent responses, Tavily query formulation, and the hermetic verifier.

```bash
# Run all tests
pytest

# Run tests with detailed verbose output
pytest -v
```

Expected output:
```
tests/test_api.py::test_home_page PASSED
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_presets_endpoint PASSED
tests/test_api.py::test_analyze_and_patch_endpoint PASSED
tests/test_api.py::test_stream_endpoint PASSED
tests/test_clients.py::test_nebius_mock_nano_triage PASSED
tests/test_clients.py::test_nebius_mock_ultra_reasoning PASSED
tests/test_clients.py::test_tavily_client_search PASSED
tests/test_config.py::test_default_settings PASSED
tests/test_config.py::test_live_settings_toggle PASSED
tests/test_pipeline.py::test_pipeline_sqli_scenario PASSED
tests/test_pipeline.py::test_pipeline_path_traversal_scenario PASSED
tests/test_pipeline.py::test_pipeline_ssrf_scenario PASSED
tests/test_pipeline.py::test_pipeline_deserialization_scenario PASSED
tests/test_verifier.py::test_syntax_checker_python_valid PASSED
tests/test_verifier.py::test_syntax_checker_python_invalid PASSED
tests/test_verifier.py::test_syntax_checker_generic_brackets PASSED
tests/test_verifier.py::test_unified_diff_validation PASSED
tests/test_verifier.py::test_patch_verifier_full_suite PASSED

============================= 19 passed in 0.83s =============================
```

---

## 🌐 Free-Tier Cloud Deployment Guide

Follow any of these recipes to deploy PatchForge live on 100% free cloud hosting:

### Option A: Hugging Face Spaces (Docker Space - 100% Free)
Hugging Face Spaces provides free 2 vCPU / 16 GB RAM instances with zero idle timeout.

1. Create a new Space at `https://huggingface.co/new-space`.
2. Choose **Docker** as the SDK and select the **Blank** template.
3. Push this repository to your Space repository:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/patchforge-nemotron
   git push space main
   ```
4. In Space **Settings -> Variables and Secrets**, add:
   - `NEBIUS_API_KEY` (Secret, optional)
   - `TAVILY_API_KEY` (Secret, optional)
   - `PORT=7860` (Hugging Face default container port)
5. The container will automatically build from the `Dockerfile` and serve on your public Space URL.

---

### Option B: Render.com / Railway / Fly.io (Free Container Web Service)
1. Fork or push this repository to GitHub.
2. Sign in to **Render** (`https://dashboard.render.com`) -> **New + Web Service**.
3. Connect your GitHub repository.
4. Render will detect the `Dockerfile`:
   - **Environment:** Docker
   - **Instance Type:** Free (512 MB RAM, 0.1 CPU)
   - **Health Check Path:** `/api/health`
5. Click **Create Web Service**. Your app is live with automatic SSL (`https://patchforge-nemotron.onrender.com`).

---

### Option C: Oracle Cloud Always-Free VM (Ubuntu / ARM Ampere)
Oracle Cloud provides Always-Free ARM instances (4 OCPUs, 24 GB RAM) and AMD micro instances.

1. SSH into your Always-Free compute instance:
   ```bash
   ssh ubuntu@<YOUR_INSTANCE_IP>
   ```
2. Install Docker and Docker Compose (or Git + Python 3.11):
   ```bash
   sudo apt-get update && sudo apt-get install -y docker.io docker-compose git
   ```
3. Clone and run with Docker Compose:
   ```bash
   git clone https://github.com/ArtyormSatori/nebius-patchforge.git
   cd nebius-patchforge
   docker-compose up -d
   ```
4. Open port `8000` on your Oracle Cloud Security List / UFW:
   ```bash
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
   sudo netfilter-persistent save
   ```
5. Access your live instance at `http://<YOUR_INSTANCE_IP>:8000`.

---

## 📡 API Reference & Integration

### 1. System Health
```http
GET /api/health
```
```json
{
  "status": "healthy",
  "service": "PatchForge-Nemotron",
  "nebius": {
    "api_base": "https://api.studio.nebius.ai/v1",
    "is_live": false,
    "mode": "Simulation Mock (Awaiting User API Key)",
    "models": {
      "fast_tier": "nvidia/nemotron-mini-4b-instruct",
      "reasoning_tier": "nvidia/nemotron-4-340b-instruct"
    }
  },
  "tavily": {
    "is_live": false,
    "mode": "Simulation Mock (Awaiting User API Key)"
  }
}
```

### 2. List Security Presets
```http
GET /api/presets
```

### 3. Analyze & Patch (REST)
```http
POST /api/patch/analyze
Content-Type: application/json

{
  "title": "SQL Injection in User Search",
  "error_log": "OperationalError: near 'OR': syntax error",
  "code_context": "cursor.execute(f'SELECT * FROM users WHERE name = \"{query}\"')",
  "file_path": "app/models/user.py",
  "language": "python",
  "enable_tavily_search": true
}
```

### 4. Real-time Live Pipeline Streaming (SSE)
```http
POST /api/patch/stream
Content-Type: application/json
Accept: text/event-stream
```
Streams live event payloads (`job_started`, `triage_completed`, `search_completed`, `reasoning_completed`, `verification_completed`, `job_finished`).

### 5. Download Raw Unified Patch
```http
GET /api/patch/jobs/{job_id}/download
```
Returns a `text/x-diff` attachment file `job-xxxx.patch`.

---

## 🎬 Video Demo & Submission Walkthrough Script (3 Minutes)

- **0:00 - 0:30 (Problem & Vision):**
  - Modern software repositories suffer from endless vulnerability alerts and bug backlogs. Human triage takes hours; single-step LLM generators hallucinate or generate non-functional diffs.
- **0:30 - 1:15 (The Solution - Dual-Tier Nemotron + Tavily):**
  - Show how PatchForge-Nemotron combines the speed of **Nemotron Mini** on Nebius for AST log classification with the deep multi-hop reasoning of **Nemotron 70B/340B** and live threat intelligence from **Tavily**.
- **1:15 - 2:00 (Live Interactive Demo):**
  - Select preset **SSRF (CWE-918)** or **Insecure Deserialization (CWE-502)**.
  - Watch the DAG nodes illuminate in real time via Server-Sent Events.
  - Review the live Tavily OWASP advisory cards retrieved in milliseconds.
- **2:00 - 2:40 (Verification & Patch Diff):**
  - Inspect the surgical unified diff. Show the **diff statistics badge** (`+8 / -2 lines`).
  - Demonstrate the **Hermetic Verifier**: AST syntax checked, tests passed, zero regressions.
  - Click **Download .patch** and copy to clipboard.
- **2:40 - 3:00 (Engineering Rigor & Deployment):**
  - Highlight the 19 passing unit tests (`pytest`), Docker containerization, and free-tier cloud readiness.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
