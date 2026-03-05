import pytest
from wuiw.intake import get_rss
from unittest.mock import MagicMock, patch

def test_required_fields_present():
    """
    entries = get_rss(RSS_URL)
    assert isinstance(entries, dict)
    """
    mock_feed = MagicMock()
    mock_feed.status = 200
    mock_feed.entries = [
        {
            "id": "123/abc",
            "junk": "no parsed_modified key"
        }
    ]

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed), \
         patch("wuiw.intake.load_modified", return_value=None), \
         patch("wuiw.intake.save_modified", return_value=None):
    
        result = get_rss("http://example.com/rss")
        
    assert result == {}


def test_date_parsing_valid():
    pass

def test_only_town_council_entries():
    pass