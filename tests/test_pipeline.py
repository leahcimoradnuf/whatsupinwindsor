import pytest
import time
import json
from unittest.mock import MagicMock, patch
from wuiw.intake import get_rss
from wuiw.editor import save_assignments, save_articles, assign, update_status
from wuiw.writer import write_article
from wuiw.config import STATUS_ASSIGNED, STATUS_DONE, STATUS_COMPLETE, STATUS_PARTIAL
from wuiw.main import main

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
        mock_fetch.return_value = ([{"doc_type": "minutes", "text": "fake transcript text", "status": "sourced", "error": None}],
                                   STATUS_ASSIGNED, 
                                   None,
                                   1)
        mock_provider.summarize.return_value = ({
                    "meeting_date": "2026-01-20",
                    "doc_type": "minutes",
                    "headline": "Test Headline",
                    "bullets": ["bullet 1", "bullet 2"],
                    "blurb": "Test blurb"
                }, "OK", 1000, 100)
        mock_provider.model = "gpt-4o-mini"
        
        for assignment in assignments:
            summarized = 0
            # mock reporter        
            documents, status, error, count = mock_fetch(assignment["materials"])

            # 5. mock writer
            articles = []
            for doc in documents:
                doc_type = doc["doc_type"]
                text = doc["text"]

                save_articles(initial_save=True, doc_type=doc_type, id=assignment["meeting_id"])
                
                article, status, error = write_article(assignment["meeting_id"], text, doc_type)
                print(f"article: {article}")
                print(f"status: {status}")
                print(f"error: {error}")
                articles.append((article, status, error))
                if status == STATUS_DONE:
                    summarized += 1

            # 6. save articles
            # for article in articles:
            #     print(article)
                # sample = (article[0]['meeting_id'], article[1], article[0]['meeting_date'], article[0]['byline'], article[0]["doc_type"], json.dumps(article[0]['summary']))
                # print(f"SAMPLE: {sample}")
            
            save_articles(articles) #TODO refactor

            if summarized == count and count != 0:
                update_status(article["meeting_id"], STATUS_COMPLETE, None) # TODO: need to derive assignment level error if some docs fail
            elif summarized < count and count != 0:
                update_status(article["meeting_id"], STATUS_PARTIAL, "summarized < count")
    
    # 7. assert article in DB
    cur = editor_db.cursor()

    # both articles written to articles table
    cur.execute("SELECT meeting_id FROM articles")
    results = cur.fetchall()
    assert len(results) == 4 # two new plus seeded assignment

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

def test_v06_pipeline(editor_db, mock_feedparser, mock_request, mock_anthropic_client, no_sleep_till_brooklyn, mock_email):
    """run main with all outgoing http/rss/sdk requests patched"""
    # first run
    main()
    
    # assertions
    # run_id = 1 across tables
    cur = editor_db.cursor()
    cur.execute("SELECT id FROM intake_records")
    result =  cur.fetchone()
    assert len(result) ==1
    assert result[0] == 1

    cur.execute("SELECT run_id FROM civic_requests")
    assert cur.fetchone()[0] == 1

    cur.execute("SELECT run_id FROM ai_requests")
    assert cur.fetchone()[0] == 1

    cur.execute("SELECT last_run_id FROM assignments WHERE meeting_id = %s", ("town_council_1419_2026",))
    assert cur.fetchone()[0] == 1

    # second run
    main()

    # # assertions
    # run_id 2 added, run 1 not overwritten
    cur.execute("SELECT id FROM intake_records")
    result2 = cur.fetchall()
    assert len(result2) == 2
    # print(f"{result2 = }")
    assert result2[0][0] == 1
    assert result2[1][0] == 2

    cur.execute("SELECT run_id FROM civic_requests")
    civic_result = cur.fetchall()
    # print(f"{civic_result = }")
    # expected result: [(1,), (1,), (1,), (1,), (1,), (2,)]
    assert civic_result[0][0] == 1 # first rss ping finds two assignment packets
    assert civic_result[1][0] == 1 # first materials.html request
    assert civic_result[2][0] == 1 # first pdf request
    assert civic_result[3][0] == 1 # second materials.html request
    assert civic_result[4][0] == 1 # second pdf request
    assert civic_result[5][0] == 2 # rss ping on run 2 finds no new rss entries, no further requests expected

    cur.execute("SELECT run_id FROM ai_requests")
    ai_result = cur.fetchall()
    # print(f"{ai_result = }")
    # expected result: [(1,), (1,)]
    assert ai_result[0][0] == 1 # ai summary request for first article in run 1
    assert ai_result[1][0] == 1 # ai summary request for second article in run 1
    # no summaries in run 2 because get_rss() finds no new leads

    cur.execute("SELECT last_run_id FROM assignments")
    assignment_results = cur.fetchall()
    # print(f"{assignment_results = }")
    # expected result: [(None,), (None,), (1,), (1,)]
    assert assignment_results[0][0] == None # manually seeded entry not tied to scraper run
    assert assignment_results[1][0] == None # manually seeded entry not tied to scraper run
    assert assignment_results[2][0] == 1 # assignment found in run one and unchanged by run 2
    assert assignment_results[3][0] == 1 # assignment found in run one and unchanged by run 2