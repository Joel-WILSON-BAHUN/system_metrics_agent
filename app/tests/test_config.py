import pytest

from app.config import Settings


def test_defaults(monkeypatch):
    monkeypatch.delenv("METRICS_ENDPOINT", raising=False)
    monkeypatch.delenv("COLLECTION_INTERVAL", raising=False)
    monkeypatch.delenv("REQUEST_TIMEOUT", raising=False)

    settings = Settings.from_env()

    assert settings.metrics_endpoint == "http://127.0.0.1:8000/metrics"
    assert settings.collection_interval == 5.0
    assert settings.request_timeout == 5.0


def test_custom_values(monkeypatch):
    monkeypatch.setenv("METRICS_ENDPOINT", "http://api:8000/metrics")
    monkeypatch.setenv("COLLECTION_INTERVAL", "2")
    monkeypatch.setenv("REQUEST_TIMEOUT", "3")

    settings = Settings.from_env()

    assert settings.metrics_endpoint == "http://api:8000/metrics"
    assert settings.collection_interval == 2.0
    assert settings.request_timeout == 3.0


def test_non_numeric_value(monkeypatch):
    monkeypatch.setenv("COLLECTION_INTERVAL", "abc")

    with pytest.raises(ValueError):
        Settings.from_env()


def test_non_positive_value(monkeypatch):
    monkeypatch.setenv("REQUEST_TIMEOUT", "0")

    with pytest.raises(ValueError):
        Settings.from_env()
