import pytest
import socket
from unittest.mock import patch, MagicMock
from wuiw.intake import get_rss, load_modified
from wuiw.intake import STATE_FILE


def test_non_200_response():
    """test for exception raised"""
    mock_feed = MagicMock()
    mock_feed.status = 500

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed), \
         patch("wuiw.intake.load_modified", return_value=None):
        
        with pytest.raises(Exception):
            get_rss("http://example.com/rss")

def test_timeout_handled():
    with patch("wuiw.intake.feedparser.parse", side_effect=socket.timeout("timed out")), \
         patch("wuiw.intake.load_modified", return_value=None):
        
        with pytest.raises(socket.timeout):
            get_rss("http://example.com/rss")

def test_missing_state_file(tmp_path, monkeypatch):
    temp_file = tmp_path / STATE_FILE
    monkeypatch.setattr("wuiw.intake.STATE_FILE", str(temp_file))

    assert load_modified() == None