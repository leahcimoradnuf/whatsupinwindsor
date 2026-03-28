import psycopg2
import psycopg2.extras
import json
from wuiw.config import get_db_connection
from wuiw.config import STATUS_PENDING, STATUS_ASSIGNED, STATUS_COMPLETE, STATUS_FAILED

def update_status(meeting_id, status, error_message=None):
    """Update status of an assignment in the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    if error_message:
        cur.execute("UPDATE assignments SET status = %s, error_message = %s where meeting_id=%s", (status, error_message, meeting_id))
    else:
        cur.execute("UPDATE assignments SET status = %s, error_message = NULL WHERE meeting_id = %s", (status, meeting_id))
    conn.commit()
    cur.close()
    conn.close()

def save_assignments(rss_assignments):
    """Add new assignments from intake.get_rss() to the assignments table"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for assignment in rss_assignments:
            cur.execute(
                """INSERT INTO assignments (meeting_id, meeting_type, published_date, materials, status)
                VALUES (%s, %s, %s, %s, 'pending')
                ON CONFLICT (meeting_id) DO UPDATE SET
                    meeting_type=EXCLUDED.meeting_type,
                    materials=EXCLUDED.materials,
                    published_date=EXCLUDED.published_date,
                    status='pending'
                WHERE assignments.materials != EXCLUDED.materials
                """, (assignment['meeting_id'], assignment['meeting_type'], assignment['published_date'], assignment['materials'])
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def assign():
    """Review db for assignments with status=STATUS_PENDING and send tasks to reporter.fetch_documents()
    Returns list of dicts"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            """SELECT assignments.meeting_id, meeting_type, materials, status
            FROM assignments
            LEFT JOIN articles ON assignments.meeting_id = articles.meeting_id
            WHERE assignments.status = 'pending' AND articles.meeting_id IS NULL;
            """
        )
        assignments = cur.fetchall()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    for assignment in assignments:
        update_status(assignment['meeting_id'], STATUS_ASSIGNED)

    return assignments

def save_articles(articles):
    """Recieve articles from writer.write_article() and add them to the articles table"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for article in articles:
            cur.execute(
                """
                INSERT INTO articles (meeting_id, meeting_date, byline, doc_type, summary)
                VALUES  (%s, %s, %s,  %s, %s)
                ON CONFLICT (meeting_id, doc_type) DO UPDATE SET
                    summary = EXCLUDED.summary,
                    meeting_date = EXCLUDED.meeting_date
                """,
                (article['meeting_id'], article['meeting_date'], article['byline'], article["doc_type"], json.dumps(article['summary']))
            )
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()