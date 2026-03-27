from dotenv import load_dotenv
load_dotenv()
import pytest
import subprocess
import time

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
    cur.execute("""CREATE TABLE assignments (...)""")
    cur.execute("""CREATE TABLE articles (...)""")
    conn.commit()
    yield conn
    cur.execute("DROP TABLE articles")
    cur.execute("DROP TABLE assignments")
    conn.commit()
    cur.close()
    conn.close()