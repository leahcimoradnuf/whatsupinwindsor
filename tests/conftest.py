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
from tests.seed import SeedData, create_tables, seed_db, cleanup

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
    create_tables(conn)
    yield UnclosableConnection(conn)
    cleanup(conn)

@pytest.fixture
def seeded_db(db_conn):
    seed_db(db_conn)
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
        provider.summarize.return_value = ({"headline": "Test", "bullets": ["item"], "blurb": "Blurb", "meeting_date": "2026-04-20"}, "OK", 100, 10)
        yield provider

@pytest.fixture
def client(db_conn):
    app.config["TESTING"] = True
    with patch("wuiw.app.get_db_connection", return_value=db_conn):
        with app.test_client() as client:
            yield client

@pytest.fixture
def seeded_client(seeded_db):
    app.config["TESTING"] = True
    with patch("wuiw.app.get_db_connection", return_value=seeded_db):
        with app.test_client() as client:
            yield client

@pytest.fixture 
def no_sleep_till_brooklyn():
    with patch("time.sleep"):
        yield

@pytest.fixture
def mock_anthropic_client():
  with patch("wuiw.journalist.Anthropic") as mock_anthropic:
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_response = MagicMock()
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 10
    mock_response.content[0].text = '{"headline": "Test", "bullets": ["item"], "blurb": "Blurb", "meeting_date": "2026-04-20"}'
    mock_client.messages.create.return_value = mock_response
    yield mock_response

@pytest.fixture
def mock_openai_client():
  with patch("wuiw.journalist.OpenAI") as mock_openai:
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 10
    mock_response.choices[0].message.content = '{"test": "article text"}'
    mock_client.messages.create.return_value = mock_response
    yield mock_response

@pytest.fixture(autouse=True)
def reset_provider():
    import wuiw.config as config
    config._provider = None
    yield
    config._provider = None

@pytest.fixture
def mock_feedparser():
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
        yield mock_feed

@pytest.fixture
def mock_request():
    mock_response = MagicMock()
    mock_response.text = open("tests/fixtures/sample_materials.html", "r").read() 
    mock_response.content = open("tests/fixtures/sample_minutes.pdf", "rb").read()
    mock_response.status_code = 200
    with patch("wuiw.reporter.requests.get", return_value=mock_response):
        yield mock_response

@pytest.fixture
def mock_email():
    with patch("wuiw.editor.smtplib.SMTP_SSL") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        yield mock_smtp

@pytest.fixture
def admin_client(client):
    with client.session_transaction() as sess:
        sess['admin'] = True
    yield client