from dotenv import load_dotenv
load_dotenv()
import pytest
import subprocess
import time
import os
import psycopg2
import json
from unittest.mock import patch, MagicMock
from wuiw.app import app
from tests.seed import SeedData

# Classes

class UnclosableConnection:
    def __init__(self, conn):
        self._conn = conn
    
    def __getattr__(self, name):
        return getattr(self._conn, name)
    
    def close(self):
        pass  # no-op

# Fixtures

@pytest.fixture
def file_server():
    proc = subprocess.Popen(
        ["python", "-m", "http.server", "8000"],
        cwd="tests/fixtures"
    )
    time.sleep(1)  # give it a moment to start
    yield
    proc.terminate()

@pytest.fixture
def db_conn():
    conn = psycopg2.connect(os.getenv("TEST_DATABASE_URL"))
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS assignments (
        id SERIAL PRIMARY KEY,
        meeting_id TEXT UNIQUE NOT NULL,
        meeting_type TEXT,
        body TEXT,
        published_date DATE,
        materials TEXT,
        status TEXT DEFAULT 'pending',
        error_message TEXT);"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        meeting_id TEXT UNIQUE NOT NULL,
        meeting_date DATE,
        byline TEXT,
        doc_type TEXT,
        summary JSONB,
        reviewed BOOLEAN DEFAULT FALSE,
        UNIQUE (meeting_id, doc_type));"""
        )
    conn.commit()
    yield UnclosableConnection(conn)
    cur.execute("DROP TABLE articles")
    cur.execute("DROP TABLE assignments")
    conn.commit()
    cur.close()
    conn.close()

@pytest.fixture
def seeded_db(db_conn):
    data = SeedData()
    cur = db_conn.cursor()
    for assignment in data.assignments:
        cur.execute(
            """INSERT INTO assignments (meeting_id, meeting_type, body, published_date, materials, status)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (assignment["meeting_id"], assignment["meeting_type"], assignment["body"], assignment["published_date"], assignment["materials"], "pending")
        )
    for article in data.articles:
        cur.execute(
            """
            INSERT INTO articles (meeting_id, meeting_date, byline, doc_type, summary, reviewed)
            VALUES  (%s, %s, %s, %s, %s, FALSE)
            ON CONFLICT (meeting_id, doc_type) DO UPDATE SET
                summary = EXCLUDED.summary,
                meeting_date = EXCLUDED.meeting_date
            """,
            (article['meeting_id'], article['meeting_date'], article['byline'], article["doc_type"], json.dumps(article['summary']))
        )
    db_conn.commit()
    yield db_conn

@pytest.fixture
def editor_db(seeded_db):
    with patch("wuiw.editor.get_db_connection", return_value=seeded_db):
        yield seeded_db

@pytest.fixture
def mock_provider():
    """mock up a connection to AI provider"""
    with patch("wuiw.writer.get_provider") as mock_get:
        provider = MagicMock()
        mock_get.return_value = provider
        yield provider

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def empty_client(db_conn):
    app.config["TESTING"] = True
    with patch("wuiw.app.get_db_connection", return_value=db_conn):
        with app.test_client() as client:
            yield client