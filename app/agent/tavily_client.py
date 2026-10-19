"""Tavily Search API client for live CVE intelligence & patch advisories."""

from typing import Optional, List
import httpx
from app.config import settings
from app.core.models import TavilySearchResult, SearchHit


class TavilySearchClient:
    """Client for querying external vulnerability databases and patch patterns via Tavily."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.tavily_api_key
        self.api_base = settings.tavily_api_base.rstrip("/")
        self.timeout = 25.0

    async def search(self, query: str, max_results: int = 3) -> TavilySearchResult:
        """Search security advisories or patch patterns."""
        if settings.is_tavily_live and self.api_key:
            return await self._live_search(query, max_results)
        return self._mock_search(query)

    async def _live_search(self, query: str, max_results: int) -> TavilySearchResult:
        """Execute live search call to Tavily API."""
        url = f"{self.api_base}/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "max_results": max_results,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

            hits: List[SearchHit] = []
            for item in data.get("results", []):
                hits.append(
                    SearchHit(
                        title=item.get("title", "Advisory"),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                    )
                )

            summary = data.get("answer", "") or (hits[0].snippet if hits else "Advisories retrieved.")
            return TavilySearchResult(query=query, results=hits, live_call=True, summary=summary)
        except Exception as e:
            # Fallback to simulated hits on failure
            res = self._mock_search(query)
            res.summary += f" (Live Tavily call failed: {str(e)}; returned fallback advisories)"
            return res

    def _mock_search(self, query: str) -> TavilySearchResult:
        """Simulate CVE advisory search results for common vulnerability types."""
        q_lower = query.lower()
        if "sql" in q_lower or "cwe-89" in q_lower:
            hits = [
                SearchHit(
                    title="OWASP SQL Injection Prevention Cheat Sheet",
                    url="https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
                    snippet="The primary defense against SQL injection is the use of parameterized queries (also known as prepared statements). Parameterization ensures that user input cannot alter the query structure.",
                ),
                SearchHit(
                    title="Python SQLite3 Documentation: Safe Query Execution",
                    url="https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries",
                    snippet="Never assemble SQL queries using Python's string operations. Instead, use the DB-API's parameter substitution by putting '?' as a placeholder.",
                ),
            ]
            summary = "Remediation consensus: Enforce parameterized queries with placeholder bindings to eliminate CWE-89 injection vector."
        elif "traversal" in q_lower or "cwe-22" in q_lower:
            hits = [
                SearchHit(
                    title="OWASP Path Traversal Prevention",
                    url="https://owasp.org/www-community/attacks/Path_Traversal",
                    snippet="Validate user input before using it to access files. Resolve absolute paths using realpath/abspath and verify that the target begins with the trusted base directory.",
                ),
                SearchHit(
                    title="CWE-22: Improper Limitation of a Pathname to a Restricted Directory",
                    url="https://cwe.mitre.org/data/definitions/22.html",
                    snippet="Ensure file paths cannot traverse above target root via ../ tokens. Use canonicalization and boundary verification.",
                ),
            ]
            summary = "Remediation consensus: Canonicalize file paths with os.path.realpath and verify base directory containment."
        elif "ssrf" in q_lower or "cwe-918" in q_lower or "webhook" in q_lower:
            hits = [
                SearchHit(
                    title="OWASP Server-Side Request Forgery Prevention Cheat Sheet",
                    url="https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html",
                    snippet="Enforce URL scheme to http/https, resolve destination hostnames, and block connections to private, loopback, or cloud instance metadata (169.254.169.254) addresses.",
                ),
                SearchHit(
                    title="CWE-918: Server-Side Request Forgery (SSRF)",
                    url="https://cwe.mitre.org/data/definitions/918.html",
                    snippet="Validate and sanitize user-supplied URLs against an explicit allowlist of domains or verify resolved IP against internal network blacklists.",
                ),
            ]
            summary = "Remediation consensus: Validate URL scheme, resolve DNS hostname, and block private/link-local/metadata IP addresses."
        elif "deserialization" in q_lower or "cwe-502" in q_lower or "pickle" in q_lower:
            hits = [
                SearchHit(
                    title="OWASP Deserialization Cheat Sheet",
                    url="https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html",
                    snippet="Do not deserialize untrusted data with formats that support arbitrary object instantiation (e.g., Python pickle). Prefer safe, data-only formats such as JSON.",
                ),
                SearchHit(
                    title="CWE-502: Deserialization of Untrusted Data",
                    url="https://cwe.mitre.org/data/definitions/502.html",
                    snippet="Avoid arbitrary code execution vulnerabilities by replacing pickle with JSON or cryptographically HMAC-signing serialized data.",
                ),
            ]
            summary = "Remediation consensus: Replace unsafe pickle deserialization with safe JSON format or authenticated cryptographic tokens."
        else:
            hits = [
                SearchHit(
                    title="Concurrency & Race Condition Mitigation Guidelines",
                    url="https://cwe.mitre.org/data/definitions/362.html",
                    snippet="Use mutex locks, atomic primitives, or database transaction isolation levels to prevent check-then-act race conditions.",
                )
            ]
            summary = "Remediation consensus: Wrap check-then-act operations inside synchronization primitives or atomic transactions."

        return TavilySearchResult(query=query, results=hits, live_call=False, summary=summary)
