import time
import pytest
import psycopg2.extras
from datetime import datetime
from unittest.mock import MagicMock, patch
from wuiw.editor import assign, update_status, save_assignments, open_intake, close_intake, save_ai_log, save_civic_log, send_alert, update_article, save_articles, record_document_count
from wuiw.config import STATUS_PENDING, STATUS_ASSIGNED, STATUS_COMPLETE, STATUS_FAILED, PROVIDER, STATUS_REPORTING, STATUS_DRAFT, STATUS_DONE
from tests.seed import SeedData
from wuiw.log import ai_log, civic_log

def test_db_fixture(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = [row[0] for row in cur.fetchall()]
    assert "assignments" in tables
    assert "articles" in tables

def test_v03_update_status(editor_db):
    update_status("town_council_1263_2026", STATUS_ASSIGNED)    
    cur = editor_db.cursor()
    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("town_council_1263_2026",))
    result = cur.fetchone()

    assert result[0] == STATUS_ASSIGNED

def test_v03_update_status_with_error(editor_db):
    update_status("town_council_1263_2026", STATUS_FAILED, "non-200 materials page response")
    cur = editor_db.cursor()
    cur.execute("SELECT error_message FROM assignments WHERE meeting_id = %s", ("town_council_1263_2026",))
    first_result = cur.fetchone()

    # error message is updated
    assert first_result[0] == "non-200 materials page response"

    # error message is cleared when new status with error_message=None is written
    update_status("town_council_1263_2026", STATUS_COMPLETE)
    cur.execute("SELECT error_message FROM assignments WHERE meeting_id = %s", ("town_council_1263_2026",))
    second_result = cur.fetchone()

    assert second_result[0] is None

def test_v03_save_new_assignments(editor_db):
    data = SeedData()
    new_assignments = data.assignments

    save_assignments(new_assignments)
    cur = editor_db.cursor()
    cur.execute("SELECT meeting_id FROM assignments")
    result = cur.fetchall()

    assert len(result) == 2 # 3 would mean there's a duplicate

    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("town_council_1263_2026",))
    assert cur.fetchone()[0] == "pending"

    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("town_council_1265_2026",))
    assert cur.fetchone()[0] == "pending"

def test_v03_save_new_material_resets_status(editor_db):
    new_assignments = [
        {
            "meeting_id": "town_council_1263_2026",
            "meeting_type": "Regular Meeting",
            "body": "Town Council",
            "published_date": "2026-01-20",
            "materials": "/link/to/new/html"
        }
    ]
    # make the status 'assigned'
    update_status("town_council_1263_2026", STATUS_COMPLETE)
    cur = editor_db.cursor()
    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("town_council_1263_2026",))
    assert cur.fetchone()[0] == "complete"

    # save the assignment with a new materials link
    save_assignments(new_assignments)
    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("town_council_1263_2026",))
    assert cur.fetchone()[0] == "pending"

def test_v03_unchanged_assignment_preserves_status(editor_db):
    # set status to complete
    update_status("town_council_1263_2026", STATUS_COMPLETE)
    data = SeedData()
    identical_assignment = data.assignments[1]
    
    # save identical data
    save_assignments([identical_assignment])
    
    cur = editor_db.cursor()
    cur.execute("SELECT status FROM assignments WHERE meeting_id = %s", ("town_council_1263_2026",))
    assert cur.fetchone()[0] == "complete"

def test_v06_open_valid_entry(editor_db):
    start = datetime.now()
    result = open_intake(start)
    cur = editor_db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM intake_records;")
    rows = cur.fetchall()
    cur.close()

    # test for started row with only start time
    assert result == 1
    assert len(rows) == 1
    row = rows[0]
    assert row["run_started_at"] == start
    assert row["run_completed_at"] == None
    assert row["status"] == None
    assert row["new_assignments"] == None
    assert row["failed_assignments"] == None
    assert row["error_message"] == None

def test_v06_close_valid_entry(editor_db):
    start = datetime.now()
    run_id = open_intake(start)
    end = datetime.now()
    close_intake(run_id, end, STATUS_COMPLETE, 3, 0)
    cur = editor_db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM intake_records;")
    rows = cur.fetchall()
    cur.close()

    # test for only one row with populated data
    assert len(rows) == 1
    row = rows[0]
    assert row["run_started_at"] == start
    assert row["run_completed_at"] == end
    assert row["status"] == STATUS_COMPLETE
    assert row["new_assignments"] == 3
    assert row["failed_assignments"] == 0
    assert row["error_message"] == None

def test_v06_write_http_request_logs(editor_db):
    """test that ai_log and civic_log data are written to the database by save_civic_log and save_ai_log"""
    start = datetime.now()
    run_id = open_intake(start)
    ai_log.reset()
    ai_log.set_run_id(1)
    ai_log.record(datetime.now(), PROVIDER, "OK", 1000, 100)
    ai_log.record(datetime.now(), PROVIDER, "OK", 2000, 100)
    ai_log.record(datetime.now(), PROVIDER, "FAIL", None, None)

    civic_log.reset()
    civic_log.set_run_id(1)
    civic_log.record(datetime.now(), "http://link/to/stuff", 200)
    civic_log.record(datetime.now(), "http://broken/link/to/stuff", 404)

    save_ai_log(ai_log.info)
    save_civic_log(civic_log.info)

    cur = editor_db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""SELECT * FROM ai_requests""")
    ai_result = cur.fetchall()
    cur.execute("""SELECT * FROM civic_requests""")
    civic_result = cur.fetchall()
    cur.close()

    for entry in [ai_result[0], civic_result[0]]:
        assert isinstance(entry["timestamp"], datetime)

    assert ai_result[1]["provider"] == "Anthropic"
    assert ai_result[1]["status"] == "OK"
    assert ai_result[1]["input_tokens"] == 2000
    assert ai_result[1]["output_tokens"] == 100
    assert ai_result[2]["status"] == "FAIL"
    assert ai_result[2]["input_tokens"] is None

    assert civic_result[0]["url"] == "http://link/to/stuff"
    assert civic_result[0]["response_status"] == 200
    assert civic_result[1]["response_status"] == 404

def test_v06_send_alert(no_sleep_till_brooklyn):
    with patch("wuiw.editor.smtplib.SMTP_SSL") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
        
        send_alert("test error")
        
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

def test_v07_update_article_pipe(admin_client, seeded_db, edit_seeded):
    # Check seeded headline
    cur = seeded_db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""SELECT summary FROM articles
                WHERE meeting_id = %s
                """, ("town_council_1263_2026",))
    selection = cur.fetchone()
    assert selection["summary"]["headline"] == "Town Council Approves $400k Bond and Settles Lawsuit"

    # verify seeded article has an unresolved error
    # Verify error status is resolved
    cur.execute("""SELECT resolved FROM error_reports
                WHERE meeting_id = %s
                """, ("town_council_1263_2026",))
    status = cur.fetchone()
    assert status["resolved"] == False

    # Make the update
    response = admin_client.post("/admin/articles/town_council_1263_2026", data=edit_seeded)
    assert response.status_code == 302
    
    # Verify the edited headline        
    cur.execute("""SELECT summary FROM articles
                WHERE meeting_id = %s
                """, ("town_council_1263_2026",))
    selection = cur.fetchone()
    assert selection["summary"]["headline"] == "Town Council Approves $400k Bond, Settles Suit, and Files TPS Reports"

    # Verify error status is resolved
    cur.execute("""SELECT resolved FROM error_reports
                WHERE meeting_id = %s
                """, ("town_council_1263_2026",))
    status = cur.fetchone()
    assert status["resolved"] == True

@pytest.mark.skip(reason="never meant to deploy")
def test_v11_initial_article_save(editor_db):
    """Test that save_articles() with initial_save=True flag inserts a row into the articles table"""
    save_articles(initial_save=True, id="town_council_1234_2026", doc_type="agenda")
    cur = editor_db.cursor()
    cur.execute("""SELECT doc_type FROM articles WHERE meeting_id = %s""", ("town_council_1234_2026",))
    assert cur.fetchone()[0] == "agenda"

    cur.execute("""SELECT status FROM articles WHERE meeting_id = %s""", ("town_council_1234_2026",))
    assert cur.fetchone()[0] == STATUS_REPORTING

def test_v11_save_articles(editor_db):
    """Save a new article after initial save has created row"""
    data = SeedData()
    save_assignments(data.assignments)
    assign()
    articles = data.articles + [({"meeting_id": "town_council_1265_2026", "doc_type": "agenda"}, STATUS_DRAFT, "error")]
    save_articles(articles)

    cur = editor_db.cursor()
    cur.execute("""SELECT status FROM articles WHERE meeting_id = %s AND doc_type = %s""", ("town_council_1265_2026", "agenda"))
    result = cur.fetchone()
    assert result[0] == STATUS_DRAFT

    cur.execute("""SELECT status FROM articles WHERE meeting_id = %s AND doc_type = %s""", ("town_council_1265_2026", "minutes"))
    result = cur.fetchone()
    assert result[0] == STATUS_DONE

    cur.execute("""SELECT status FROM articles WHERE meeting_id = %s AND doc_type = %s""", ("town_council_1265_2026", "voting_grid"))
    result = cur.fetchone()
    assert result[0] == STATUS_REPORTING

def test_v11_record_document_status(editor_db):
    record_document_count("town_council_1265_2026", 0, 0)
    cur = editor_db.cursor()
    cur.execute("""SELECT documents_available, documents_summarized, status FROM assignments
                WHERE meeting_id = %s""", ("town_council_1265_2026",)
                )
    result = cur.fetchone()
    assert result[0] == 0
    assert result[1] == 0
    assert result[2] == "partial"

    record_document_count("town_council_1265_2026", 3, 2)
    cur.execute("""SELECT documents_available, documents_summarized, status FROM assignments
                WHERE meeting_id = %s""", ("town_council_1265_2026",)
                )
    result = cur.fetchone()
    assert result[0] == 3
    assert result[1] == 2
    assert result[2] == "partial"

    record_document_count("town_council_1265_2026", 3, 3)
    cur.execute("""SELECT documents_available, documents_summarized, status FROM assignments
                WHERE meeting_id = %s""", ("town_council_1265_2026",)
                )
    result = cur.fetchone()
    assert result[0] == 3
    assert result[1] == 3
    assert result[2] == "complete"
