import pytest
from unittest.mock import MagicMock, patch
from wuiw.writer import review_article, write_article
from wuiw.config import STATUS_DONE, STATUS_DRAFT

def test_review_valid_draft():
    valid_draft = {
        "meeting_date": "2026-01-20",
        "headline": "Town Council Approves $400k Bond and Settles Lawsuit",
        "bullets": [
            "$400,000 bond for stormwater management program approved unanimously",
            "Council endorses the proposed 2025 Plan of Conservation and Development",
            "Public concerns raised about police department staffing and management",
            "Fire prevention poster contest awards presented to school students",
            "Upcoming public meetings on automated license plate readers and Senior Olympics announced",
            "Settlement of Rivers Bend lawsuit agreed upon during Executive Session"
        ],
        "blurb": "The Windsor Town Council's meeting on January 20 saw the approval of a $400,000 bond for stormwater management, alongside unanimous endorsement of the updated 2025 Plan of Conservation and Development. Public commentary reflected concerns regarding police staffing and management practices. The council recognized students from local schools for their achievements in fire safety awareness with a poster contest. A settlement regarding the Rivers Bend lawsuit was also discussed and ratified in Executive Session. Additionally, upcoming community events, including a public meeting on automated license plate readers, were highlighted."
    }
    reviewed = review_article(valid_draft)
    assert isinstance(reviewed, tuple)
    assert reviewed[0] == valid_draft
    assert reviewed[1] == STATUS_DONE
    assert reviewed[2] == None

def test_review_draft_not_dict():
    invalid_draft = [{
        "meeting_date": "2026-01-20",
        "headline": "Town Council Approves $400k Bond and Settles Lawsuit",
        "bullets": [
            "$400,000 bond for stormwater management program approved unanimously",
            "Council endorses the proposed 2025 Plan of Conservation and Development",
            "Public concerns raised about police department staffing and management",
            "Fire prevention poster contest awards presented to school students",
            "Upcoming public meetings on automated license plate readers and Senior Olympics announced",
            "Settlement of Rivers Bend lawsuit agreed upon during Executive Session"
        ],
        "blurb": "The Windsor Town Council's meeting on January 20 saw the approval of a $400,000 bond for stormwater management, alongside unanimous endorsement of the updated 2025 Plan of Conservation and Development. Public commentary reflected concerns regarding police staffing and management practices. The council recognized students from local schools for their achievements in fire safety awareness with a poster contest. A settlement regarding the Rivers Bend lawsuit was also discussed and ratified in Executive Session. Additionally, upcoming community events, including a public meeting on automated license plate readers, were highlighted."
    }]
    reviewed = review_article(invalid_draft)
    assert isinstance(reviewed, tuple)
    assert reviewed[0] == None
    assert reviewed[1] == STATUS_DRAFT
    assert reviewed[2] == "draft is not a dict"

def test_review_draft_missing_keys():
    invalid_keys_draft = {
        "meeting_date": "2026-01-20",
        "bullets": [
            "$400,000 bond for stormwater management program approved unanimously",
            "Council endorses the proposed 2025 Plan of Conservation and Development",
            "Public concerns raised about police department staffing and management",
            "Fire prevention poster contest awards presented to school students",
            "Upcoming public meetings on automated license plate readers and Senior Olympics announced",
            "Settlement of Rivers Bend lawsuit agreed upon during Executive Session"
        ],
        "blurb": "The Windsor Town Council's meeting on January 20 saw the approval of a $400,000 bond for stormwater management, alongside unanimous endorsement of the updated 2025 Plan of Conservation and Development. Public commentary reflected concerns regarding police staffing and management practices. The council recognized students from local schools for their achievements in fire safety awareness with a poster contest. A settlement regarding the Rivers Bend lawsuit was also discussed and ratified in Executive Session. Additionally, upcoming community events, including a public meeting on automated license plate readers, were highlighted."
    }
    reviewed = review_article(invalid_keys_draft)
    assert isinstance(reviewed, tuple)
    assert reviewed[0] == None
    assert reviewed[1] == STATUS_DRAFT
    assert reviewed[2] == "missing keys: {'headline'}"

def test_review_bad_date_format():
    invalid_date_draft_1 = {
        "meeting_date": "01-20-2026",
        "headline": "",
        "bullets": [],
        "blurb": ""
    }
    invalid_date_draft_2 = {
        "meeting_date": "2026-27-01",
        "headline": "",
        "bullets": [],
        "blurb": ""
    }
    review_1 = review_article(invalid_date_draft_1)
    assert isinstance(review_1, tuple)
    assert review_1[0] == None
    assert review_1[1] == STATUS_DRAFT
    assert review_1[2] == "date: 01-20-2026 not in format YYYY-MM-DD"

    review_2 = review_article(invalid_date_draft_2)
    assert isinstance(review_2, tuple)
    assert review_2[0] == None
    assert review_2[1] == STATUS_DRAFT
    assert review_2[2] == "date: 2026-27-01 not in format YYYY-MM-DD"

def test_review_bullets_not_list():
    invalid_bullets_draft = {
        "meeting_date": "2026-01-20",
        "headline": "",
        "bullets": ("bullet1", "bullet2"),
        "blurb": ""
    }
    reviewed = review_article(invalid_bullets_draft)
    assert isinstance(reviewed, tuple)
    assert reviewed[0] == None
    assert reviewed[1] == STATUS_DRAFT
    assert reviewed[2] == "bullets is not a list"

def test_write_returns_valid_tuple(mock_provider):
    mock_provider.summarize.return_value = ({
        "meeting_date": "2026-01-20",
        "headline": "Test Headline",
        "bullets": ["bullet 1", "bullet 2"],
        "blurb": "Test blurb"
    }, "OK", 1000, 100)
    mock_provider.model = "gpt-4o-mini"
    
    result = write_article("town_council_1234_2026", "raw text", "minutes")
    print(result[2])
    assert result[1] == STATUS_DONE
    assert result[2] == None
    assert result[0]["meeting_id"] == "town_council_1234_2026"
    assert result[0]["byline"] == "gpt-4o-mini"
    assert result[0]["doc_type"] == "minutes"

def test_write_returns_failed(mock_provider):
    # summarize returns bad data to trigger review_article failure
    mock_provider.summarize.return_value = "not a dict"
    mock_provider.model = "gpt-4o-mini"

    result = write_article("town_council_1234_2026", "raw text", "minutes")
    assert result[0] == None
    assert result[1] == STATUS_DRAFT
    assert result[2] is not None  # some error message present

def test_metadata_not_returned_on_failed(mock_provider):
    mock_provider.summarize.return_value = "not a dict"
    mock_provider.model = "gpt-4o-mini"

    result = write_article("town_council_1234_2026", "raw text", "minutes")
    assert result[0] is None  # no article
    # meeting_id and byline should never have been added