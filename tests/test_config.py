"""Unit tests for configuration."""

from app.config import Settings


def test_default_settings():
    s = Settings(force_mock=True)
    assert "nvidia/nemotron" in s.nebius_model_reasoning.lower()
    assert "nvidia/nemotron" in s.nebius_model_fast.lower()
    assert s.is_nebius_live is False
    assert s.is_tavily_live is False


def test_live_settings_toggle():
    s = Settings(nebius_api_key="valid-test-key", force_mock=False)
    assert s.is_nebius_live is True

    s_mock = Settings(nebius_api_key="valid-test-key", force_mock=True)
    assert s_mock.is_nebius_live is False
