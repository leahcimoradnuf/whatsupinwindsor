import os
import psycopg2
import psycopg2.extras
from flask import Flask, url_for
from wuiw.editor import update_article
from unittest.mock import MagicMock, patch
from wuiw.app import app
from bs4 import BeautifulSoup

# Test Auth
def test_v07_admin_route_redirects_when_not_logged_in(client):
    response = client.get("/admin")
    assert response.status_code == 302

def test_v07_login_get_renders_form(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_v07_login_post_correct_password(client):
    response = client.post("/login", data={"passkey": os.getenv("ADMIN-PASSWORD")})
    assert response.status_code == 302

def test_v07_login_post_wrong_password(client):
    response = client.post("/login", data={"passkey": "wrongpassword"})
    assert response.status_code == 302
    # should redirect back to login, not dashboard

def test_v07_admin_accessible_when_logged_in(admin_client):
    response = admin_client.get("/admin")
    assert response.status_code == 200

def test_v07_logout_clears_session(admin_client):
    admin_client.get("/logout")
    response = admin_client.get("/admin")
    assert response.status_code == 302

# Test New Admin Routes
def test_v07_admin_article_edit(admin_client, seeded_db):
    response = admin_client.get("/admin/articles/town_council_1263_2026")
    assert response.status_code == 200

def test_v07_admin_article_edit(client, seeded_db):
    response = client.get("/admin/articles/town_council_1263_2026")
    assert response.status_code == 302

def test_v07_admin_view(admin_client, seeded_db):
    response = admin_client.get("/")
    assert response.status_code == 200

def test_v07_submit_edits(admin_client, seeded_db):
    with patch("wuiw.app.update_article") as update:
        response = admin_client.post("/admin/articles/town_council_1263_2026",
                                     data={
                                         "headline": "The Pope went to McDonalds",
                                         "meeting_type": "Special Meeting",
                                         "date": "2026-05-19",
                                         "bullets": ["bullet 1", "bullet 2"],
                                         "blurb": "Pope John IV visited the Vatican Mickey-Dees and got a quarter-pounder with cheese."
                                     })
        assert response.status_code == 302
        update.assert_called_once()

def test_v07_publish_article(admin_client, seeded_db):
    with patch("wuiw.app.publish_article") as publish:
        # unpublish first
        response = admin_client.post("/admin/articles/town_council_1263_2026/publish", data={"published": "false"})
        assert response.status_code == 302
        publish.assert_called()

        # then re-publish
        response = admin_client.post("/admin/articles/town_council_1263_2026/publish", data={"published": "true"})
        assert response.status_code == 302
        publish.assert_called()

def test_v07_approve_article(admin_client, seeded_db):
    with patch("wuiw.app.approve_article") as approve:
        # approve
        response = admin_client.post("/admin/articles/town_council_1263_2026/approve", data={"reviewed": "true"})
        assert response.status_code == 302
        approve.assert_called()

        # unapprove
        response = admin_client.post("/admin/articles/town_council_1263_2026/approve", data={"reviewed": "false"})
        assert response.status_code == 302
        approve.assert_called()

# Test error reporting
def test_v07_report_error_pipe(client, seeded_db):
    response = client.post("/report-error", data={
        "meeting_id": "town_council_1263_2026",
        "feedback": "This summary contains an error"
        })
    assert response.status_code == 200

    # Verify error was reported
    cur = seeded_db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""SELECT report_text FROM error_reports
                WHERE meeting_id = %s
                """, ("town_council_1263_2026",))
    messages = cur.fetchall()
    assert len(messages) == 2
    assert messages[-1]['report_text'] == "This summary contains an error"

# Test manual document fetch
def test_v07_non_admin_run(client):
    response = client.post("/admin/run")
    assert response.status_code == 302
    with app.app_context():
        assert response.location.startswith('/login')

def test_v07_fetch_main(admin_client):
    with patch("wuiw.app.main") as run:
        response = admin_client.post("/admin/run")
        assert response.status_code == 302
        run.assert_called_once()

# Test error data is rendered 
def test_v07_edit_article_errors(admin_client, seeded_db):
    """Check that an article with known errors renders them in a table beneath the editing field
    """
    response = admin_client.get("/admin/articles/town_council_1263_2026")
    soup = BeautifulSoup(response.data, "html.parser")
    # there should be a table
    tr = soup.find_all("tr")
    assert len(tr) > 0