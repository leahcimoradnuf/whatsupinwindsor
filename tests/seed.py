import psycopg2
import os
import json
from wuiw.config import STATUS_DONE, STATUS_PENDING

# data

PROMPTS = "/home/mike/myprojects/whatsupinwindsor/wuiw/prompts.json"

class SeedData:
    def __init__(self):
        self.assignments = [
            {
                "meeting_id": "town_council_1265_2026",
                "meeting_type": "regular meeting",
                "body": "town council",
                "published_date": "2026-01-05",
                "materials": "https://www.windsorct.gov/AgendaCenter/ViewFile/Agenda/_01052026-1262?html=true",
            },{
                "meeting_id": "town_council_1263_2026",
                "meeting_type": "regular meeting",
                "body": "town council",
                "published_date": "2026-01-20",
                "materials": "https://www.windsorct.gov/AgendaCenter/ViewFile/Agenda/_01202026-1263?html=true"
            }
        ]
        # articles data
        self.articles = [(
            {
                "meeting_id": "town_council_1265_2026",
                "doc_type": "minutes",
                "byline": "gpt-4o-mini",
                "meeting_date": "2026-01-05",
                "summary": {
                    "meeting_date": "2026-01-05",
                    "headline": "Council Honors 250th Anniversary, Addresses Surveillance Concerns",
                    "bullets": [
                        "Proclamation presented for the 250th Anniversary of the Declaration of Independence",
                        "Public expressed concerns about the Flock surveillance cameras and their implications",
                        "Council approved amended ALPR Data Usage and Security Policy",
                        "Introduced a bond ordinance for $400,000 for stormwater management",
                        "Set a public hearing for the stormwater bond ordinance on January 20, 2026",
                        "Resolutions regarding inclusion in the Highlands Conservation Act tabled for further discussion",
                        "Multiple appointments to various boards and commissions approved"
                    ],
                    "blurb": "During the meeting, Mayor Black-Burke presented a proclamation celebrating the upcoming 250th anniversary of the signing of the Declaration of Independence, urging community engagement in related events. Public comments centered on growing concerns regarding surveillance through the Flock camera system, prompting the Council to commit to further public engagement. The Council approved an amended policy for Automated License Plate Reader use and introduced a significant bond ordinance for stormwater management projects. Additionally, several appointments to local commissions and boards were approved without objection."
                    }
            }, STATUS_DONE, None, "http://link/"),({
                "meeting_id": "town_council_1263_2026",
                "doc_type":"minutes",
                "byline": "gpt-4o-mini",
                "meeting_date": "2026-01-20",
                "summary": {
                    "meeting_date": "2026-01-20",
                    "headline": "Town Council Approves $400k Bond and Settles Lawsuit",
                    "bullets": [
                        "$400,000 bond for stormwater management program approved unanimously",
                        "Council endorses the proposed 2025 Plan of Conservation and Development",
                        "Public concerns raised about police department staffing and management",
                        "Fire prevention poster contest awards presented to school students",
                        "Upcoming public meetings on automated license plate readers and Senior Olympics announced",
                        "Settlement of Rivers Bend lawsuit agreed upon during Executive Session"
                    ],
                    "blurb": "The Windsor Town Council's meeting on January 20 saw the approval of a $400,000 bond for stormwater management, alongside unanimous endorsement of the updated 2025 Plan of Conservation and Development. Public commentary reflected concerns regarding police staffing and management practices. The council recognized students from local schools for their achievements in fire safety awareness with a poster contest. A settlement regarding the Rivers Bend lawsuit was also discussed and ratified in Executive Session. Additionally, upcoming community events, including a public meeting on automated license plate readers, were highlighted."
                }
            },STATUS_DONE, None, "http://link/")
        ]

        self.errors = [
            {
                "meeting_id": "town_council_1263_2026",
                "report_text": "You forgot the TPS report."
            }
        ]

    def load_prompts(self, file):
        with open(file, 'r') as f:
            prompts = json.loads(f.read())
        return prompts


def spool_up(url):
    print("connect() called")
    try:
        conn = psycopg2.connect(url)
        print("connected")
    except Exception as e:
        print(f"connection failed: {e}")
        return None
    return conn

def create_tables(conn):
    print("create_tables() called")
    # create tables
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS intake_records (
        id SERIAL PRIMARY KEY,
        run_started_at TIMESTAMP,
        run_completed_at TIMESTAMP,
        status TEXT,
        new_assignments INT,
        failed_assignments INT,
        error_message TEXT);"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS assignments (
        id SERIAL PRIMARY KEY,
        meeting_id TEXT UNIQUE NOT NULL,
        meeting_type TEXT,
        body TEXT,
        published_date DATE,
        materials TEXT,
        last_run_id INT REFERENCES intake_records (id),
        documents_summarized INT,
        documents_available INT,
        status TEXT DEFAULT 'pending',
        error_message TEXT,
        reviewed BOOLEAN DEFAULT FALSE,
        published BOOLEAN DEFAULT TRUE);"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS civic_requests (
        id SERIAL PRIMARY KEY,
        run_id INT REFERENCES intake_records (id),
        timestamp TIMESTAMP,
        url TEXT,
        response_status INT);"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS ai_requests (
        id SERIAL PRIMARY KEY,
        run_id INT REFERENCES intake_records (id),
        timestamp TIMESTAMP,
        provider TEXT,
        status TEXT,
        input_tokens INT,
        output_tokens INT);"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        meeting_id TEXT NOT NULL,
        status TEXT,
        doc_url TEXT,
        meeting_date DATE,
        byline TEXT,
        doc_type TEXT,
        summary JSONB,
        UNIQUE (meeting_id, doc_type));"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS error_reports (
        id SERIAL PRIMARY KEY,
        meeting_id TEXT REFERENCES assignments(meeting_id),
        report_text TEXT,
        submitted_at TIMESTAMP DEFAULT NOW(),
        resolved BOOLEAN DEFAULT FALSE
        );"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS system_prompts (
        id SERIAL PRIMARY KEY,
        doc_type TEXT UNIQUE NOT NULL,
        content TEXT NOT NULL
        );"""
        )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS few_shot_examples (
        id SERIAL PRIMARY KEY,
        meeting_id TEXT UNIQUE NOT NULL,
        doc_type TEXT NOT NULL,
        document_text TEXT NOT NULL,
        meeting_date DATE,
        expected_output JSONB NOT NULL,
        UNIQUE (meeting_id, doc_type));;"""
        )

    conn.commit()
    cur.close()


def seed_db(conn):
    print("seed_db() called")
    cur = conn.cursor()
    # get seed data
    data = SeedData()
    prompts = data.load_prompts(PROMPTS)

    # seed data
    for assignment in data.assignments:
        cur.execute(
            """INSERT INTO assignments (meeting_id, meeting_type, body, published_date, materials, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (meeting_id) DO NOTHING""",
            (assignment["meeting_id"], assignment["meeting_type"], assignment["body"], assignment["published_date"], assignment["materials"], STATUS_PENDING)
        
        )
    for article in data.articles:
        cur.execute(
            """
            INSERT INTO articles (meeting_id, status, meeting_date, byline, doc_type, summary)
            VALUES  (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (meeting_id, doc_type) DO UPDATE SET
                summary = EXCLUDED.summary,
                meeting_date = EXCLUDED.meeting_date
            """,
            (article[0]['meeting_id'], article[1], article[0]['meeting_date'], article[0]['byline'], article[0]["doc_type"], json.dumps(article[0]['summary']))
        )
    for error in data.errors:
        cur.execute(
            """INSERT INTO error_reports (meeting_id, report_text)
            VALUES (%s, %s)""",
            (error['meeting_id'], error['report_text'])
        )
    
    # System prompt for minutes
    # TODO build out for other doc types when necessary
    cur.execute(
            """INSERT INTO system_prompts (doc_type, content)
            VALUES (%s, %s)
            ON CONFLICT (doc_type) DO UPDATE SET
                content = EXCLUDED.content
            """,
            ("minutes", prompts["minutes"]["system"])
        )
    
    for few_shot in prompts["minutes"]["examples"]:
        doc_type = "minutes"
        expected_output = {
            "meeting_date": few_shot["meeting_date"],
            "meeting_id": few_shot["meeting_id"],
            "headline": few_shot["headline"],
            "bullets": few_shot["bullets"],
            "blurb": few_shot["blurb"]
        }
        cur.execute(
            """INSERT INTO few_shot_examples (meeting_id, doc_type, document_text, meeting_date, expected_output)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (meeting_id) DO UPDATE SET
                document_text = EXCLUDED.document_text,
                expected_output = EXCLUDED.expected_output
            """,
            (few_shot["meeting_id"], doc_type, few_shot["minutes_text"], few_shot["meeting_date"], json.dumps(expected_output))
        )

    conn.commit()
    cur.close()
    # conn.close()
    
def cleanup(conn):
    # conn = psycopg2.connect(os.getenv("TEST_DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("DROP TABLE articles")
    cur.execute("DROP TABLE error_reports")
    cur.execute("DROP TABLE ai_requests")
    cur.execute("DROP TABLE civic_requests")
    cur.execute("DROP TABLE assignments")
    cur.execute("DROP TABLE intake_records")
    cur.execute("DROP TABLE system_prompts")
    cur.execute("DROP TABLE few_shot_examples")
    conn.commit()
    cur.close()
    conn.close()