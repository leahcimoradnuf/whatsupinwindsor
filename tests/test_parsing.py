import pytest
from wuiw.intake import get_rss, classify
from unittest.mock import MagicMock, patch
from wuiw.config import MUNICIPAL_BODIES

def test_bad_entries_handled():
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

def test_required_fields_present():
    pass

def test_date_parsing_valid():
    pass

def test_classify_body():
    """Classify gov body based on meeting title"""
    entries = [
        "Town Council Regular Meeting",
        "Town Council Public Hearing",
        "Planning & Zoning Commission Regular Meeting",
        "Hamburgers & Hotdogs Club Biennial Feast"
        ]
    
    bodies = []
    for entry in entries:
        bodies.append(classify(entry, MUNICIPAL_BODIES, threshold=75))

    assert bodies == ["Town Council", "Town Council", "Planning Commission", None]


