from unittest.mock import MagicMock, patch
from wuiw.editor import update_status
from wuiw.config import STATUS_PENDING, STATUS_ASSIGNED, STATUS_COMPLETE, STATUS_FAILED

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