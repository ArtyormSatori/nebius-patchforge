"""Nebius Token Factory client with fallback to intelligent mock simulation."""

import json
import re
import time
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings


class NebiusTokenFactoryClient:
    """Client for Nebius Token Factory API serving NVIDIA Nemotron models."""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.api_key = api_key or settings.nebius_api_key
        self.api_base = (api_base or settings.nebius_api_base).rstrip("/")
        self.timeout = 60.0

    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute chat completion via Nebius Token Factory or intelligent mock."""
        start_time = time.perf_counter()

        if settings.is_nebius_live and self.api_key:
            return await self._live_call(model, messages, temperature, max_tokens, response_format, start_time)

        # Fallback to local high-fidelity mock simulation
        return await self._mock_call(model, messages, start_time)

    async def _live_call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, str]],
        start_time: float,
    ) -> Dict[str, Any]:
        """Make HTTP call to Nebius Token Factory endpoint."""
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        content = data["choices"][0]["message"]["content"]
        return {
            "content": content,
            "model": model,
            "latency_ms": latency_ms,
            "is_mock": False,
            "raw_response": data,
        }

    async def _mock_call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        start_time: float,
    ) -> Dict[str, Any]:
        """High-fidelity simulation of NVIDIA Nemotron models for development & offline evaluation."""
        user_prompt = ""
        system_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt += msg["content"] + "\n"
            elif msg["role"] == "user":
                user_prompt += msg["content"] + "\n"

        latency_ms = (time.perf_counter() - start_time) * 1000.0 + 45.0  # simulate realistic latency

        # Check if Tier 1 Triage (Nemotron Nano) or Tier 2 Reasoning (Nemotron Ultra)
        if "nemotron-nano" in model.lower() or "nano" in model.lower() or "fast" in model.lower():
            content = self._simulate_nemotron_nano_triage(user_prompt)
        else:
            content = self._simulate_nemotron_ultra_reasoning(user_prompt)

        return {
            "content": content,
            "model": f"{model} (Simulated Mock - Awaiting User Key)",
            "latency_ms": latency_ms,
            "is_mock": True,
        }

    def _simulate_nemotron_nano_triage(self, prompt: str) -> str:
        """Simulate Tier 1 fast triage output (JSON format)."""
        prompt_lower = prompt.lower()
        if "sql" in prompt_lower or "cwe-89" in prompt_lower:
            return json.dumps({
                "error_type": "SQLInjection",
                "summary": "Detected unescaped user string interpolation in SQL query construction.",
                "severity": "CRITICAL",
                "suspect_lines": [14],
                "syntax_valid": True,
                "confidence_score": 0.98,
            })
        elif "traversal" in prompt_lower or "cwe-22" in prompt_lower:
            return json.dumps({
                "error_type": "PathTraversal",
                "summary": "Target accepts arbitrary user input into file path resolution without boundary check.",
                "severity": "CRITICAL",
                "suspect_lines": [10],
                "syntax_valid": True,
                "confidence_score": 0.97,
            })
        elif "race" in prompt_lower or "balance" in prompt_lower:
            return json.dumps({
                "error_type": "ConcurrencyRaceCondition",
                "summary": "Non-atomic check-then-act pattern creates double-spend/negative balance risk.",
                "severity": "HIGH",
                "suspect_lines": [12, 14],
                "syntax_valid": True,
                "confidence_score": 0.94,
            })
        elif "ssrf" in prompt_lower or "cwe-918" in prompt_lower or "webhook" in prompt_lower:
            return json.dumps({
                "error_type": "ServerSideRequestForgery",
                "summary": "Target performs unvalidated network requests to arbitrary user-supplied URLs without loopback or metadata IP filtering.",
                "severity": "CRITICAL",
                "suspect_lines": [10, 11, 12],
                "syntax_valid": True,
                "confidence_score": 0.99,
            })
        elif "deserialization" in prompt_lower or "cwe-502" in prompt_lower or "pickle" in prompt_lower:
            return json.dumps({
                "error_type": "InsecureDeserialization",
                "summary": "Untrusted user payload is passed directly to pickle.loads leading to potential Remote Code Execution (RCE).",
                "severity": "CRITICAL",
                "suspect_lines": [9, 10],
                "syntax_valid": True,
                "confidence_score": 0.99,
            })
        else:
            return json.dumps({
                "error_type": "UnhandledRuntimeBug",
                "summary": "Runtime error or logic anomaly identified from input trace.",
                "severity": "HIGH",
                "suspect_lines": [1],
                "syntax_valid": True,
                "confidence_score": 0.90,
            })

    def _simulate_nemotron_ultra_reasoning(self, prompt: str) -> str:
        """Simulate Tier 2 deep reasoning output (JSON with RCA, unified diff, patched code, test plan)."""
        prompt_lower = prompt.lower()
        if "sql" in prompt_lower or "cwe-89" in prompt_lower:
            return json.dumps({
                "root_cause": "The SQL query in `get_user_profile` utilizes Python f-string interpolation (`f\"SELECT ... WHERE username = '{username}'\"`). An attacker can break out of the string delimiter with single quotes to inject arbitrary SQL statements (CWE-89).",
                "fix_strategy": "Refactor database query to use parameterized statements (`?` placeholders for SQLite or `%s` for PostgreSQL), passing user arguments as a separate tuple.",
                "unified_diff": """--- a/app/services/user_service.py
+++ b/app/services/user_service.py
@@ -11,4 +11,4 @@
-    query = f"SELECT id, username, email, role FROM users WHERE username = '{username}'"
-    cursor.execute(query)
+    query = "SELECT id, username, email, role FROM users WHERE username = ?"
+    cursor.execute(query, (username,))
""",
                "patched_code": """import sqlite3
from typing import Optional, Dict, Any

def get_db_connection():
    conn = sqlite3.connect(":memory:")
    return conn

def get_user_profile(username: str) -> Optional[Dict[str, Any]]:
    \"\"\"Fetch user profile by username.\"\"\"
    conn = get_db_connection()
    cursor = conn.cursor()
    # SECURE: Use parameterized queries to prevent SQL injection (CWE-89)
    query = "SELECT id, username, email, role FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "email": row[2], "role": row[3]}
    return None
""",
                "test_plan": "1. Assert that queries with payload `admin' OR 1=1--` return None and do not trigger syntax errors.\n2. Assert that legitimate username lookups continue to return valid user dicts.",
                "reasoning_steps": [
                    "Analyzed stack trace and AST: line 14 shows direct f-string injection into SQL string.",
                    "Consulted CVE advisories: Parameterized query enforcement is the canonical remediation.",
                    "Formulated parameterized replacement with tuple binding `(username,)`.",
                    "Verified syntax compatibility with sqlite3 Python standard library.",
                ],
            })
        elif "traversal" in prompt_lower or "cwe-22" in prompt_lower:
            return json.dumps({
                "root_cause": "User-supplied filename is concatenated via os.path.join without verifying that the resolved canonical path remains confined within STORAGE_DIR (CWE-22).",
                "fix_strategy": "Resolve absolute canonical paths via os.path.realpath / os.path.abspath and assert that the target path begins with STORAGE_DIR, raising PermissionError or ValueError on boundary violations.",
                "unified_diff": """--- a/app/api/downloads.py
+++ b/app/api/downloads.py
@@ -8,3 +8,6 @@
-    target_path = os.path.join(STORAGE_DIR, filename)
+    # Sanitize and guard against directory traversal attacks (CWE-22)
+    safe_path = os.path.realpath(os.path.join(STORAGE_DIR, filename))
+    if not safe_path.startswith(os.path.realpath(STORAGE_DIR)):
+        raise PermissionError("Access denied: Path traversal detected")
+    target_path = safe_path
""",
                "patched_code": """import os

STORAGE_DIR = "/var/app/data/uploads"

def download_file(filename: str) -> bytes:
    \"\"\"Retrieve uploaded file content.\"\"\"
    # SECURE: Enforce canonical directory boundary check (CWE-22 mitigation)
    safe_path = os.path.realpath(os.path.join(STORAGE_DIR, filename))
    if not safe_path.startswith(os.path.realpath(STORAGE_DIR)):
        raise PermissionError("Access denied: Path traversal detected")
    with open(safe_path, "rb") as f:
        return f.read()
""",
                "test_plan": "1. Test with `../../../../etc/passwd` to ensure PermissionError is raised.\n2. Test with legitimate file inside STORAGE_DIR to ensure file reads cleanly.",
                "reasoning_steps": [
                    "Identified lack of path normalization in download handler.",
                    "Applied os.path.realpath boundary assertion.",
                    "Ensured clean exception propagation on invalid access.",
                ],
            })
        elif "ssrf" in prompt_lower or "cwe-918" in prompt_lower or "webhook" in prompt_lower:
            return json.dumps({
                "root_cause": "The application sends HTTP requests to arbitrary user-controlled endpoints using urllib.request without validating scheme or blocking internal private IP ranges (127.0.0.1, 169.254.169.254, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16).",
                "fix_strategy": "Validate URL scheme to allow only https/http, resolve target IP hostname and reject loopback, link-local metadata, or RFC 1918 private IP addresses before initiating connection.",
                "unified_diff": """--- a/app/services/webhook.py
+++ b/app/services/webhook.py
@@ -1,4 +1,7 @@
 import urllib.request
+from urllib.parse import urlparse
+import ipaddress
+import socket
 import json
 from typing import Dict, Any

+def is_safe_webhook_url(url: str) -> bool:
+    parsed = urlparse(url)
+    if parsed.scheme not in ('http', 'https'):
+        return False
+    hostname = parsed.hostname
+    if not hostname:
+        return False
+    try:
+        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
+        return not (ip.is_private or ip.is_loopback or ip.is_link_local)
+    except Exception:
+        return False
+
 def trigger_webhook(webhook_url: str, payload: Dict[str, Any]) -> int:
     \"\"\"Send JSON payload notification to user-configured webhook URL.\"\"\"
-    # VULNERABLE: Direct request to user-supplied URL without private IP filtering or scheme check
+    if not is_safe_webhook_url(webhook_url):
+        raise ValueError(f"Prohibited webhook target or internal IP address: {webhook_url}")
     req = urllib.request.Request(
         webhook_url,
         data=json.dumps(payload).encode('utf-8'),
         headers={'Content-Type': 'application/json'}
     )
     with urllib.request.urlopen(req, timeout=5) as resp:
         return resp.status
""",
                "patched_code": """import urllib.request
from urllib.parse import urlparse
import ipaddress
import socket
import json
from typing import Dict, Any

def is_safe_webhook_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(hostname))
        return not (ip.is_private or ip.is_loopback or ip.is_link_local)
    except Exception:
        return False

def trigger_webhook(webhook_url: str, payload: Dict[str, Any]) -> int:
    \"\"\"Send JSON payload notification to user-configured webhook URL.\"\"\"
    if not is_safe_webhook_url(webhook_url):
        raise ValueError(f"Prohibited webhook target or internal IP address: {webhook_url}")
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status
""",
                "test_plan": "1. Assert ValueError is raised when attempting to target 169.254.169.254 or localhost.\\n2. Assert normal public HTTPS targets succeed.",
                "reasoning_steps": [
                    "Identified lack of IP verification on user-supplied webhook endpoint.",
                    "Referenced OWASP SSRF Prevention Cheat Sheet and CVE patterns via Tavily.",
                    "Implemented DNS resolution check against private and link-local address spaces.",
                    "Replaced direct connection with guarded check.",
                ],
            })
        elif "deserialization" in prompt_lower or "cwe-502" in prompt_lower or "pickle" in prompt_lower:
            return json.dumps({
                "root_cause": "The parse_session_token function uses Python's standard pickle module to deserialize arbitrary client data, which allows arbitrary code execution via constructed __reduce__ methods.",
                "fix_strategy": "Replace unsafe pickle deserialization with safe, deterministic serialization such as json.loads or HMAC-signed tokens.",
                "unified_diff": """--- a/app/security/session.py
+++ b/app/security/session.py
@@ -1,6 +1,6 @@
 import base64
-import pickle
+import json
 from typing import Dict, Any

 def parse_session_token(token_b64: str) -> Dict[str, Any]:
     \"\"\"Decode and deserialize client session token.\"\"\"
-    # VULNERABLE: Insecure deserialization via pickle allows Remote Code Execution
+    # SECURE: Safe JSON parsing replacing unsafe pickle deserialization (CWE-502)
     raw_data = base64.b64decode(token_b64)
-    session_data = pickle.loads(raw_data)
+    session_data = json.loads(raw_data.decode('utf-8'))
     return session_data
""",
                "patched_code": """import base64
import json
from typing import Dict, Any

def parse_session_token(token_b64: str) -> Dict[str, Any]:
    \"\"\"Decode and deserialize client session token.\"\"\"
    # SECURE: Safe JSON parsing replacing unsafe pickle deserialization (CWE-502)
    raw_data = base64.b64decode(token_b64)
    session_data = json.loads(raw_data.decode('utf-8'))
    return session_data
""",
                "test_plan": "1. Verify valid JSON-encoded base64 tokens deserialize into dicts.\\n2. Verify malicious pickle byte sequences fail with json.JSONDecodeError rather than executing code.",
                "reasoning_steps": [
                    "Flagged pickle.loads as inherently insecure for untrusted network input.",
                    "Queried Tavily for CWE-502 remediation standards in web session handling.",
                    "Swapped pickle for strict json.loads with UTF-8 decoding.",
                    "AST syntax verification confirmed zero regressions.",
                ],
            })
        else:
            return json.dumps({
                "root_cause": "Race condition in non-atomic check-then-act execution flow.",
                "fix_strategy": "Introduce threading.Lock or atomic transaction boundary around wallet balance inspection and deduction.",
                "unified_diff": """--- a/app/billing/wallet.py
+++ b/app/billing/wallet.py
@@ -3,2 +3,3 @@
+import threading
 from typing import Dict

+wallet_lock = threading.Lock()
@@ -10,4 +12,5 @@
-    current_balance = user_wallets.get(user_id, 0.0)
-    if current_balance >= amount:
-        time.sleep(0.01)
-        user_wallets[user_id] = current_balance - amount
-        return True
+    with wallet_lock:
+        current_balance = user_wallets.get(user_id, 0.0)
+        if current_balance >= amount:
+            user_wallets[user_id] = current_balance - amount
+            return True
""",
                "patched_code": """import time
import threading
from typing import Dict

user_wallets: Dict[str, float] = {"user_1": 100.0}
wallet_lock = threading.Lock()

def process_withdrawal(user_id: str, amount: float) -> bool:
    \"\"\"Deduct balance from user wallet with thread-safe lock.\"\"\"
    with wallet_lock:
        current_balance = user_wallets.get(user_id, 0.0)
        if current_balance >= amount:
            user_wallets[user_id] = current_balance - amount
            return True
    return False
""",
                "test_plan": "1. Spawn 10 concurrent threads attempting $20 withdrawal from $100 wallet.\n2. Verify exactly 5 succeed and final balance is 0.0 (no negative balance).",
                "reasoning_steps": [
                    "Located thread unsafe shared memory access in `process_withdrawal`.",
                    "Introduced reentrant/standard mutex lock synchronization.",
                    "Eliminated artificial delay inside critical section.",
                ],
            })
