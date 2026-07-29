from wuiw.util import classify


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
        bodies.append(classify(entry, town_id="windsorct", class_type="municipal_body", threshold=75))

    assert bodies == ["town_council", "town_council", "planning_commission", "unclassified"]

def test_v11_classify_doc_types():
    """Classify document types"""
    entries = [
        "Town Council Unapproved Meeting Minutes",
        "01_15_2026 - Draft Minutes",
        "Special Meeting Voting Grid",
        "Town council 01_15_2026-VG",
        "Board of Education Action Grid",
        "Town Council 01-15-2026 AGENDA",
        "Planning commission actions"
    ]

    result = []
    for entry in entries:
        result.append(classify(entry, town_id="windsorct", class_type="doc_type"))

    assert result == ["minutes", "minutes", "voting_grid", "voting_grid", "voting_grid", "agenda", "voting_grid"]

def test_v11_classify_meeting_types():
    """Classify meeting types"""
    entries = [
        "Town Council Regular Meeting",
        "Town Council Public Hearing",
        "Planning & Zoning Commission Regular Meeting",
        "Hamburgers & Hotdogs Club Biennial Feast",
        "Board of Education Special Meeting"
        ]
    
    result = []
    for entry in entries:
        result.append(classify(entry, town_id="windsorct", class_type="meeting_type"))

    assert result == ["regular_meeting", "public_hearing", "regular_meeting", "unclassified", "special_meeting"]