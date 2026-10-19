"""Preset real-world bug scenarios for demo and testing."""

from typing import List, Dict, Any

PRESET_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "cwe-89-sqli",
        "title": "CWE-89: SQL Injection in User Profile Lookup",
        "language": "python",
        "file_path": "app/services/user_service.py",
        "error_log": """[SECURITY_AUDIT_ALERT] CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')
Source: Vulnerability Scanner / Dynamic DAST
Location: app/services/user_service.py:line 14
Trace:
  File "app/services/user_service.py", line 14, in get_user_profile
    query = f"SELECT id, username, email, role FROM users WHERE username = '{username}'"
sqlite3.OperationalError: near "admin'--": syntax error
Attack payload: username="admin' OR 1=1--" bypasses authentication and exposes all rows.""",
        "code_context": """import sqlite3
from typing import Optional, Dict, Any

def get_db_connection():
    conn = sqlite3.connect(":memory:")
    return conn

def get_user_profile(username: str) -> Optional[Dict[str, Any]]:
    \"\"\"Fetch user profile by username.\"\"\"
    conn = get_db_connection()
    cursor = conn.cursor()
    # VULNERABLE: Direct string formatting into SQL query
    query = f"SELECT id, username, email, role FROM users WHERE username = '{username}'"
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "email": row[2], "role": row[3]}
    return None
""",
    },
    {
        "id": "cwe-22-path-traversal",
        "title": "CWE-22: Path Traversal in File Download Handler",
        "language": "python",
        "file_path": "app/api/downloads.py",
        "error_log": """[SECURITY_SCAN] Critical Finding: CWE-22 Path Traversal
Path: app/api/downloads.py:line 12
Evidence: Target accepts user-controlled 'filename' parameter directly into os.path.join
Exploit Vector: filename="../../../../etc/passwd"
Result: File content outside STORAGE_DIR leaked to unauthenticated caller.""",
        "code_context": """import os

STORAGE_DIR = "/var/app/data/uploads"

def download_file(filename: str) -> bytes:
    \"\"\"Retrieve uploaded file content.\"\"\"
    # VULNERABLE: Lack of path sanitization allows directory traversal attacks
    target_path = os.path.join(STORAGE_DIR, filename)
    with open(target_path, "rb") as f:
        return f.read()
""",
    },
    {
        "id": "concurrency-race-condition",
        "title": "Race Condition in Wallet Balance Deduction",
        "language": "python",
        "file_path": "app/billing/wallet.py",
        "error_log": """[SRE_CRITICAL_INCIDENT] Race condition detected in concurrent checkout
Traceback (most recent call last):
  File "app/billing/wallet.py", line 22, in process_withdrawal
    raise NegativeBalanceError("Wallet balance cannot be negative!")
NegativeBalanceError: Wallet balance cannot be negative! Account #8812 balance: -45.00
Root cause: Check-then-act without lock synchronization allows double-spend under high concurrency.""",
        "code_context": """import time
from typing import Dict

user_wallets: Dict[str, float] = {"user_1": 100.0}

def process_withdrawal(user_id: str, amount: float) -> bool:
    \"\"\"Deduct balance from user wallet.\"\"\"
    current_balance = user_wallets.get(user_id, 0.0)
    # VULNERABLE: Check-then-act without locking or atomic deduction
    if current_balance >= amount:
        time.sleep(0.01)  # Simulate I/O latency
        user_wallets[user_id] = current_balance - amount
        return True
    return False
""",
    },
]
