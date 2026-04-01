import pytest
import socket
from unittest.mock import patch, MagicMock
from wuiw.intake import get_rss


def test_v01_non_200_response():
    """test for exception raised"""
    mock_feed = MagicMock()
    mock_feed.status = 500

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed):
        
        with pytest.raises(Exception):
            get_rss("http://example.com/rss")

def test_v01_timeout_handled():
    with patch("wuiw.intake.feedparser.parse", side_effect=socket.timeout("timed out")):
        
        with pytest.raises(socket.timeout):
            get_rss("http://example.com/rss")
