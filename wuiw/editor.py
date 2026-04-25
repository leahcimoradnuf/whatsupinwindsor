import psycopg2
import psycopg2.extras
import json
import logging
import smtplib
import os
from email.mime.text import MIMEText
from wuiw.config import get_db_connection
from wuiw.config import STATUS_ASSIGNED

logger = logging.getLogger(__name__)

def update_status(meeting_id, status, error_message=None):
    """Update status of an assignment in the database"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if error_message:
            cur.execute("UPDATE assignments SET status = %s, error_message = %s where meeting_id=%s", (status, error_message, meeting_id))
        else:
            cur.execute("UPDATE assignments SET status = %s, error_message = NULL WHERE meeting_id = %s", (status, meeting_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
       if cur: cur.close()
       if conn: conn.close()

def save_assignments(rss_assignments, run_id=None):
    """Add new assignments from intake.get_rss() to the assignments table"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for assignment in rss_assignments:
            cur.execute(
                """INSERT INTO assignments (meeting_id, meeting_type, body, published_date, materials, last_run_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (meeting_id) DO UPDATE SET
                    meeting_type=EXCLUDED.meeting_type,
                    materials=EXCLUDED.materials,
                    body=EXCLUDED.body,
                    published_date=EXCLUDED.published_date,
                    status='pending',
                    last_run_id=EXCLUDED.last_run_id
                WHERE assignments.materials != EXCLUDED.materials
                """, (assignment['meeting_id'], assignment['meeting_type'], assignment['body'], assignment['published_date'], assignment['materials'], run_id)
                )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def assign():
    """Review db for assignments with status=STATUS_PENDING and send tasks to reporter.fetch_documents()
    Returns list of dicts"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """SELECT assignments.meeting_id, meeting_type, materials, status
            FROM assignments
            LEFT JOIN articles ON assignments.meeting_id = articles.meeting_id
            WHERE assignments.status = 'pending' AND articles.meeting_id IS NULL;
            """
        )
        assignments = cur.fetchall()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

    for assignment in assignments:
        update_status(assignment['meeting_id'], STATUS_ASSIGNED)

    return assignments

def save_articles(articles):
    """Recieve articles from writer.write_article() and add them to the articles table"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for article in articles:
            cur.execute(
                """
                INSERT INTO articles (meeting_id, meeting_date, byline, doc_type, summary)
                VALUES  (%s, %s, %s, %s, %s)
                ON CONFLICT (meeting_id, doc_type) DO UPDATE SET
                    summary = EXCLUDED.summary,
                    meeting_date = EXCLUDED.meeting_date
                """,
                (article['meeting_id'], article['meeting_date'], article['byline'], article["doc_type"], json.dumps(article['summary']))
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def open_intake(start):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO intake_records (run_started_at)
                    VALUES (%s)
                    RETURNING id;""", (start,))
        run_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()
    
    return run_id

def close_intake(run_id, stop, status, new_assignments, failed_assignments, error=None):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""UPDATE intake_records
                    SET run_completed_at = %s,
                        status = %s,
                        new_assignments = %s,
                        failed_assignments = %s,
                        error_message = %s
                    WHERE id = %s;""",
                    (stop, status, new_assignments, failed_assignments, error, run_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def save_civic_log(logs):
    """save outgoing request logs to town servers
    log is a list of tuples returned by civic_log.info"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for log in logs:
            try:
                cur.execute("""
                            INSERT INTO civic_requests (run_id, timestamp, url, response_status)
                            VALUES (%s, %s, %s, %s)""",
                            (log[0], log[1], log[2], log[3]))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.warning(f"{e}")
                continue
    finally:    
        if cur: cur.close()
        if conn: conn.close()

def save_ai_log(logs):
    """save outgoing request logs to ai providers
    log is a list of tuples returned by ai_log.info"""
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for log in logs:
            try:
                cur.execute("""
                            INSERT INTO ai_requests (run_id, timestamp, provider, status, input_tokens, output_tokens)
                            VALUES (%s, %s, %s, %s, %s, %s)""",
                            (log[0], log[1], log[2], log[3], log[4], log[5]))
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.warning(f"{e}")
                continue
    finally:
        if cur: cur.close()
        if conn: conn.close()

def send_alert(error):
    sender = os.getenv("ALERT_EMAIL")
    password = os.getenv("ALERT_EMAIL_PASSWORD")
    recipient = os.getenv("ALERT_EMAIL")  # send to yourself

    msg = MIMEText(f"WUIW pipeline failed.\n\nError: {error}")
    msg["Subject"] = "WUIW Pipeline Failure"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        logger.info("Failure alert sent")
    except Exception as e:
        logger.error("Failed to send alert: %s", e)

def update_article(meeting_id, updates):
    """saves edits, sets reviewed = True, optionally resolves all open error reports
    updates is type dict and is constructed by the POST route when updates are submitted

    Data structure of updates:
        {
        "assignment": {
            "meeting_type": "Regular Meeting"
        },
        "articles": {
            "agenda": {
                "items": ["items"]
            },
            "minutes": {
                "meeting_date": "2025-03-01",
                "headline": "headline",
                "bullets": ["bullets"],
                "blurb": "blurb"
                }
            }
        }
    """
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # update assignments.meeting_type
        cur.execute("""UPDATE assignments SET meeting_type = %s WHERE meeting_id = %s""",
                    (updates["assignment"]["meeting_type"], meeting_id))

        # update articles.meeting_date and articles.summary
        for doc_type, data in updates["articles"].items():
            if doc_type == "agenda":
                pass

            if doc_type == "minutes":
                cur.execute("""UPDATE articles SET
                            summary = %s,
                            meeting_date = %s
                            WHERE meeting_id = %s AND doc_type = %s""",
                            (data, data["meeting_date"], meeting_id, doc_type))

            if doc_type == "voting_grid":
                pass

        # update assignments.reviewed
        cur.execute("""UPDATE assignments SET reviewed = TRUE
                    WHERE meeting_id = %s""",
                    (meeting_id,))

        # update error_reports.status
        cur.execute("""UPDATE error_reports SET resolved = TRUE
                    WHERE meeting_id = %s""",
                    (meeting_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.warning(f"{e}")
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

def report_error(meeting_id, error_text):
    """inserts a new row to error_reports"""
    pass

def publish_article(meeting_id, published=True):
    """sets published boolean on an assignment"""
    pass