import psycopg2
import os
from wuiw.editor import save_assignments, save_articles
from wuiw.config import get_db_connection

# connect to test db and create tables
# conn = get_db_connection()
# cur = conn.cursor()
# cur.execute(
#     """CREATE TABLE IF NOT EXISTS assignments (
#     id SERIAL PRIMARY KEY,
#     meeting_id TEXT UNIQUE NOT NULL,
#     meeting_type TEXT,
#     body TEXT,
#     published_date DATE,
#     materials TEXT,
#     status TEXT DEFAULT 'pending',
#     error_message TEXT);"""
#     )
# cur.execute(
#     """CREATE TABLE IF NOT EXISTS articles (
#     id SERIAL PRIMARY KEY,
#     meeting_id TEXT UNIQUE NOT NULL,
#     meeting_date DATE,
#     byline TEXT,
#     doc_type TEXT,
#     summary JSONB,
#     UNIQUE (meeting_id, doc_type));"""
#     )
# conn.commit()
# cur.close()
# conn.close()

# use editor.py functions to populate the tables

# assignments data
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
        self.articles = [
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
            },{
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
            }
        ]

# add to database
# data = SeedData()
# save_assignments(data.assignments)
# try:
#     save_articles(data.articles)
#     print("articles saved")
# except Exception as e:
#     print(f"articles not saved: {e}")