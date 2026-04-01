from wuiw.intake import get_rss, classify
from unittest.mock import MagicMock, patch
from wuiw.config import MUNICIPAL_BODIES

def test_v01_bad_entries_handled():
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

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed):
    
        result = get_rss("http://example.com/rss")

    assert result == []

def test_v01_required_fields_present():
    mock_feed = MagicMock()
    mock_feed.status = 200
    mock_feed.modified_parsed = None
    mock_feed.entries = [
        {
            "id": "http://www.windsorct.gov/AgendaCenter/1419/",
            "title": "Town Council Regular Meeting",
            "published_parsed": (2026, 1, 15, 0, 0, 0)
        },
        {
            "id": "http://www.windsorct.gov/AgendaCenter/5643/",
            "title": "Flying Spaghetti Monster Club",
            "published_parsed": (2025, 10, 1, 0, 0, 0)
        }
    ]

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed):
        
        result = get_rss("http://example.com/rss")

    # Test first entry is output correctly
    assert len(result) == 2
    assert result[0]["meeting_id"] == "town_council_1419_2026"
    assert result[0]["body"] == "town_council"
    assert result[0]["published_date"] == "2026-01-15"
    assert result[0]["materials"] == "https://www.windsorct.gov/AgendaCenter/ViewFile/Agenda/_01152026-1419?html=true"

    # Test second entry unclassified title is handled
    assert result[1]["meeting_id"] == "unclassified_5643_2025"

def test_v01_date_parsing_valid():
    pass

def test_v01_classify_body():
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

    assert bodies == ["town council", "town council", "planning commission", "unclassified"]


