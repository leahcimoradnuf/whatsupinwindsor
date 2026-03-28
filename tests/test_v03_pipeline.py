import pytest
import time
from unittest.mock import MagicMock, patch
from wuiw.intake import get_rss
from wuiw.editor import save_assignments, save_articles, assign, update_status
from wuiw.writer import write_article
from wuiw.config import STATUS_ASSIGNED

def test_v03_pipeline(editor_db, mock_provider):
    # 1. mock get_rss() return
    mock_feed = MagicMock()
    mock_feed.status = 200
    mock_feed.modified_parsed = None
    mock_feed.entries = [
        {
            "id": "http://www.windsorct.gov/AgendaCenter/1419/",
            "title": "Town Council Regular Meeting",
            "published_parsed": time.strptime("2026-01-15", "%Y-%m-%d")
        },
        {
            "id": "http://www.windsorct.gov/AgendaCenter/5643/",
            "title": "Flying Spaghetti Monster Club",
            "published_parsed": time.strptime("2025-01-10", "%Y-%m-%d")
        }
    ]

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed):
        mock_rss = get_rss("http://example.com/rss")
    
    # 2. save to assignments
    save_assignments(mock_rss)
    
    # 3. get work queue
    assignments = assign()

    with patch("wuiw.reporter.fetch_documents") as mock_fetch:
        mock_fetch.return_value = (
            {"minutes": "fake transcript text"},
            STATUS_ASSIGNED,
            None
        )
        mock_provider.summarize.return_value = {
                    "meeting_date": "2026-01-20",
                    "doc_type": "minutes",
                    "headline": "Test Headline",
                    "bullets": ["bullet 1", "bullet 2"],
                    "blurb": "Test blurb"
                }
        mock_provider.model = "gpt-4o-mini"
        
        for assignment in assignments:
            # mock reporter        
            documents, status, error = mock_fetch(assignment["materials"])

            # 5. mock writer
            for doc_type, text in documents.items():
                article, status, error = write_article(assignment["meeting_id"], text, doc_type)
                print(f"article: {article}")
                print(f"status: {status}")
                print(f"error: {error}")
                # 6. save articles
                save_articles([article])
                update_status(article["meeting_id"], status, error) # TODO: this updates status for whole assignment even if only 1 of multiple documents is done
    
    # 7. assert article in DB
    cur = editor_db.cursor()

    # both articles written to articles table
    cur.execute("SELECT meeting_id FROM articles")
    results = cur.fetchall()
    assert len(results) == 3 # two new plus seeded assignment

    # specific meeting_ids present
    cur.execute("SELECT meeting_id FROM articles WHERE meeting_id = %s", ("town_council_1419_2026",))
    assert cur.fetchone() is not None

    cur.execute("SELECT meeting_id FROM articles WHERE meeting_id = %s", ("unclassified_5643_2025",))
    assert cur.fetchone() is not None

    # both assignments marked complete
    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("town_council_1419_2026",))
    assert cur.fetchone()[0] == "complete"

    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("unclassified_5643_2025",))
    assert cur.fetchone()[0] == "complete"