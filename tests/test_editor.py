from unittest.mock import MagicMock, patch
from wuiw.editor import update_status, save_assignments
from wuiw.config import STATUS_PENDING, STATUS_ASSIGNED, STATUS_COMPLETE, STATUS_FAILED
from tests.seed import SeedData

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
    # new_assignments = [
    #     {
    #         "meeting_id": "town_council_1263_2026",
    #         "meeting_type": "Regular Meeting",
    #         "body": "Town Council",
    #         "published_date": "2026-01-20",
    #         "materials": "/link/to/html"
    #     },{
    #         "meeting_id": "town_council_5643_2026",
    #         "meeting_type": "Regular Meeting",
    #         "body": "Town Council",
    #         "published_date": "2026-01-05",
    #         "materials": "/link/to/html"
    #     }
    # ]
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