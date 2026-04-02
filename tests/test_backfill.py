import os
import pytest
import requests as real_requests
from wuiw.intake import backfill
from unittest.mock import MagicMock

# Unit tests

def test_v04_backfill_valid_input(monkeypatch):
    """Happy Path returns valid data structure"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    with open("tests/fixtures/sample_backfill.html", "r") as f:
        mock_response.text = f.read()
    
    monkeypatch.setattr("wuiw.intake.requests.get", lambda url, **kwargs: mock_response)
    
    results = backfill("2026-03-01", "2026-03-31", 18)
    
    # non-zero list
    assert len(results) > 0

    # proper keys in each dict
    assert all("meeting_id" in r for r in results)
    assert all("materials" in r for r in results)
    assert all("meeting_type" in r for r in results)
    assert all("published_date" in r for r in results)
    assert all("body" in r for r in results)
    assert all(isinstance(r, dict) for r in results)

    # meeting_id format: body_sequence_year
    assert all(len(r["meeting_id"].split("_")) >= 3 for r in results)

    # materials URL is absolute
    assert all(r["materials"].startswith("https://") for r in results)

    # published_date is ISO format
    assert all(len(r["published_date"]) == 10 for r in results)
    assert all(r["published_date"][4] == "-" for r in results)

def test_v04_backfill_non200_response(monkeypatch):
    """Non 200 Response returns empty dict and logs error"""
    mock_response = MagicMock()
    mock_response.status_code = 500
       
    monkeypatch.setattr("wuiw.intake.requests.get", lambda url, **kwargs: mock_response)
    
    results = backfill("2026-03-01", "2026-03-31", 18)

    assert results == []

def test_v04_backfill_valid_response_empty(monkeypatch):
    """200 response valid html page has no meetings to assign, return empty dict"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    with open("tests/fixtures/empty_backfill.html", "r") as f:
        mock_response.text = f.read()
    
    monkeypatch.setattr("wuiw.intake.requests.get", lambda url, **kwargs: mock_response)
    
    results = backfill("2026-03-01", "2026-03-31", 18)

    assert results == []

# Integration Tests
