"""Tests for Nebius Token Factory and Tavily clients."""

import asyncio
from app.agent.nebius_client import NebiusTokenFactoryClient
from app.agent.tavily_client import TavilySearchClient


def test_nebius_mock_nano_triage():
    client = NebiusTokenFactoryClient()
    messages = [
        {"role": "system", "content": "You are fast triage agent."},
        {"role": "user", "content": "CWE-89: SQL Injection in user profile query"},
    ]
    resp = asyncio.run(
        client.chat_completion(
            model="nvidia/nemotron-nano",
            messages=messages,
        )
    )
    assert resp["is_mock"] is True
    assert "content" in resp
    assert "SQLInjection" in resp["content"] or "error_type" in resp["content"]


def test_nebius_mock_ultra_reasoning():
    client = NebiusTokenFactoryClient()
    messages = [
        {"role": "system", "content": "You are NVIDIA Nemotron 3 Ultra deep reasoning agent."},
        {"role": "user", "content": "Synthesize fix for CWE-89 SQL Injection in user_service.py"},
    ]
    resp = asyncio.run(
        client.chat_completion(
            model="nvidia/nemotron-3-ultra",
            messages=messages,
        )
    )
    assert resp["is_mock"] is True
    assert "unified_diff" in resp["content"]
    assert "root_cause" in resp["content"]


def test_tavily_client_search():
    client = TavilySearchClient()
    result = asyncio.run(client.search("CWE-89 SQL Injection Python mitigation"))
    assert result.query is not None
    assert len(result.results) > 0
    assert "parameterized" in result.summary.lower() or "injection" in result.summary.lower()
