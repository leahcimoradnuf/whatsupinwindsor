

import os
import time
import json

from unittest.mock import patch, MagicMock
from wuiw.intake import get_rss, sort_assignments, assign
from wuiw.config import STATE_FILE, ASSIGNMENT_LIST, RSS_URL, USER_AGENT, STATUS_PENDING, STATUS_ASSIGNED, STATUS_COMPLETE, STATUS_FAILED


def test_304_no_changes():
    """if the Last-Modified header of the feed is not newer than the last run, do nothing"""
    mock_feed = MagicMock()
    mock_feed.status = 304

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed), \
         patch("wuiw.intake.load_modified", return_value=None), \
         patch("wuiw.intake.save_modified") as mock_save:

        result = get_rss("http://example.com/rss")

    assert result == {}
    mock_save.assert_not_called()

def test_first_run_creates_files(tmp_path, monkeypatch):
    """if no modified_state.json or assignments.json exist, they are created"""

    # Create temporary file path
    temp_assignments = tmp_path / "assignments.json"
    temp_mod_state = tmp_path / "modified_state.json"

    # Patch ASSIGNMENT_LIST and STATE FILE to use temp file
    monkeypatch.setattr("wuiw.intake.ASSIGNMENT_LIST", str(temp_assignments))
    monkeypatch.setattr("wuiw.intake.STATE_FILE", str(temp_mod_state))
    
    # ---- Create fake feed ----
    fake_modified = time.gmtime()

    mock_entry = {
        "id": "http://example.com/Agenda/12345/",
        "published_parsed": time.gmtime()
    }

    mock_feed = MagicMock()
    mock_feed.status = 200
    mock_feed.modified_parsed = fake_modified
    mock_feed.entries = [mock_entry]

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed):

        entries = get_rss("http://example.com/rss")
        sort_assignments(entries)

    assert os.path.exists(temp_mod_state)
    assert os.path.exists(temp_assignments)

def test_modified_header_updates_state():
    """Confirm date in modified_state.json is updated to known date of new feed"""
    fake_modified = time.gmtime()

    mock_feed = MagicMock()
    mock_feed.status = 200
    mock_feed.modified_parsed = fake_modified
    mock_feed.entries = []  # required so loop doesn't break

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed) as mock_parse, \
         patch("wuiw.intake.load_modified", return_value=None), \
         patch("wuiw.intake.save_modified") as mock_save:

        result = get_rss("http://example.com/rss")

        # Assert feedparser called correctly
        mock_parse.assert_called_once_with(
            "http://example.com/rss",
            agent=USER_AGENT,
            modified=None
        )

        # Assert state was persisted
        mock_save.assert_called_once_with(fake_modified)

        # Assert output is an empty dict
        assert result == {}

def test_idempotent_double_run(tmp_path, monkeypatch):
    """Run thrice and confirm no duplicates and no second write"""

    # Create temporary file path
    temp_file = tmp_path / "assignments.json"

    # Patch ASSIGNMENT_LIST to use temp file
    monkeypatch.setattr("wuiw.intake.ASSIGNMENT_LIST", str(temp_file))

    sample_entries = {
        "123": {
            "year": 2025,
            "month": 3,
            "day": 1,
            "hour": 10,
            "minute": 30,
            "url": "http://example.com"
        }
    }

    new_entries = {
        "123": {
            "year": 2025,
            "month": 3,
            "day": 1,
            "hour": 10,
            "minute": 30,
            "url": "http://example.com",
            "status": STATUS_PENDING
        },
        "456": {
            "year": 2025,
            "month": 3,
            "day": 18,
            "hour": 10,
            "minute": 450,
            "url": "http://example2.com"
        }
    }

    updated = {
        "123": {
            "year": 2025,
            "month": 3,
            "day": 1,
            "hour": 10,
            "minute": 30,
            "url": "http://changed.com"
        }
    }

    # First run → should write
    changed_first = sort_assignments(sample_entries)
    assert changed_first is True

    with open(temp_file, "r") as f:
        data_after_first = json.load(f)

    assert len(data_after_first) == 1

    # Second run → should NOT write
    changed_second = sort_assignments(sample_entries)
    assert changed_second is False

    with open(temp_file, "r") as f:
        data_after_second = json.load(f)

    # Confirm still only one entry
    assert len(data_after_second) == 1
    assert data_after_second == data_after_first

    # Third run → should append, not duplicate
    changed_third = sort_assignments(new_entries)
    assert changed_third is True

    with open(temp_file, "r") as f:
        data_after_third = json.load(f)
    
    # Confirm now only two entries
    assert len(data_after_third) == 2

    # Confirm the first entry is still the same
    assert data_after_third["123"] == data_after_second["123"]
    # second entry (new) assignment stat should be false
    assert data_after_third["456"]["status"] == STATUS_PENDING

    # Fourth run --> new data for same ID overwrites and doesnt append
    changed_fourth = sort_assignments(updated)
    assert changed_fourth is True

    with open(temp_file, "r") as f:
        data_after_fourth = json.load(f)

    assert len(data_after_fourth) == 2
    assert data_after_fourth["123"]["url"] == "http://changed.com"
    # new data should change assignement state to False
    assert data_after_fourth["123"]["status"] == STATUS_PENDING

def test_assignment_state_handler(tmp_path, monkeypatch):
    """test assign() interaction with assignments file"""
    # set temporary file
    temp_file = tmp_path / "assignments.json"
    # Patch ASSIGNMENT_LIST to use temp file
    monkeypatch.setattr("wuiw.intake.ASSIGNMENT_LIST", str(temp_file))

    initial_data = {
        "123": {
            "year": 2025,
            "month": 3,
            "day": 1,
            "hour": 10,
            "minute": 30,
            "url": "http://example.com",
            "status": STATUS_PENDING
        },
        "456": {
            "year": 2025,
            "month": 3,
            "day": 18,
            "hour": 10,
            "minute": 45,
            "url": "http://example2.com",
            "status": STATUS_PENDING
        },
        "789": {
            "year": 2025,
            "month": 2,
            "day": 18,
            "hour": 1,
            "minute": 45,
            "url": "http://example3.com",
            "status": STATUS_ASSIGNED
        },
        "101": {
            "year": 2025,
            "month": 1,
            "day": 11,
            "hour": 3,
            "minute": 30,
            "url": "http://example4.com",
            "status": STATUS_COMPLETE
        },
        "000": {
            "year": 2025,
            "month": 1,
            "day": 30,
            "hour": 11,
            "minute": 12,
            "url": "http://example5.com",
            "status": STATUS_FAILED
        }
    }

    # write initial file
    with open(temp_file, "w") as f:
        json.dump(initial_data, f)

    tasks = assign()

    assert len(tasks) == 2
    assert isinstance(tasks, list) # task should be a list of tuples
    assert isinstance(tasks[0], tuple) # each entry should be a tuple
    assert ("123", "http://example.com") in tasks
    assert ("456", "http://example2.com") in tasks

    # read assignments file, status should now be assigned
    with open(temp_file, "r") as f:
        data_after_assigned = json.load(f)

    assert data_after_assigned["123"]["status"] == STATUS_ASSIGNED
    assert data_after_assigned["456"]["status"] == STATUS_ASSIGNED

    # read assignments file once more, no changes, assign returns an empty list
    no_new_tasks = assign()

    assert no_new_tasks == []
