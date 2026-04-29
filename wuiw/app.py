import psycopg2
import psycopg2.extras
import os
import logging
from flask import Flask, render_template, abort, redirect, url_for
from flask import request, session
from wuiw.config import get_db_connection
from functools import wraps

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""SELECT 
                    assignments.meeting_id,
                    assignments.meeting_type,
                    assignments.materials,
                    assignments.reviewed,
                    assignments.published,
                    articles.meeting_date,
                    articles.byline,
                    articles.summary
                FROM assignments
                JOIN articles ON assignments.meeting_id = articles.meeting_id
                WHERE articles.doc_type = 'minutes'
                AND assignments.published = TRUE""")
    articles = cur.fetchall()
    cur.close()
    conn.close()
    for article in articles:
        article["meeting_date"] = article["meeting_date"].strftime("%Y-%m-%d")

    sorted_articles = sorted(articles, key=lambda item: item['meeting_date'], reverse=True)
    return render_template("index.html", articles=sorted_articles)

@app.route("/articles")
def article_index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
                SELECT summary, meeting_date, meeting_id FROM articles;
                """)
    articles = cur.fetchall()
    cur.close()
    conn.close()
    for article in articles:
        article["meeting_date"] = article["meeting_date"].strftime("%Y-%m-%d")

    sorted_articles = sorted(articles, key=lambda item: item['meeting_date'], reverse=True)
    return render_template("article_list.html", articles=sorted_articles)

@app.route("/articles/<meeting_id>")
def article(meeting_id):
    # render single article
    conn = get_db_connection() 
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
    cur.execute("""
                SELECT
                    assignments.meeting_type,
                    assignments.materials,
                    articles.meeting_date,
                    articles.byline,
                    articles.summary
                FROM assignments
                JOIN articles ON assignments.meeting_id = articles.meeting_id
                WHERE assignments.meeting_id = %s AND articles.doc_type = 'minutes';
        """, (meeting_id,))
    article = cur.fetchone()
    cur.close()
    conn.close()
    if article is None:
         abort(404)
    return render_template("article.html", article=article)

@app.route("/report-error")
def report_error():
    return render_template("report_error.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['passkey']
        if password == os.getenv("ADMIN-PASSWORD"):
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    
    return render_template("/admin_login.html")

@app.route("/logout")
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for("index"))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
        

@app.route("/admin")
@login_required
def admin_dashboard():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""SQL see above""")
        tasks = cur.fetchall()
    except Exception as e:
        logger.warning(e)
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

    # order tasks by priority (most errors, then published)
    sorted_tasks = sorted(
        tasks, 
        key=lambda item: (-item['error_count'], not item['published'])
        )

    # render the page
    return render_template("dashboard.html", tasks=sorted_tasks)

@app.route("/admin/articles/<meeting_id>", method=["GET", "POST"])
@login_required
def article(meeting_id):
    # render single article
    conn = None
    cur = None
    try:
        conn = get_db_connection() 
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
        cur.execute("""
                    SELECT
                        assignments.meeting_type,
                        assignments.materials,
                        articles.meeting_date,
                        articles.byline,
                        articles.summary
                    FROM assignments
                    JOIN articles ON assignments.meeting_id = articles.meeting_id
                    WHERE assignments.meeting_id = %s AND articles.doc_type = 'minutes';
            """, (meeting_id,))
        article = cur.fetchone()
        cur.execute("""
                    SELECT report_text, submitted_at 
                    FROM error_reports
                    WHERE meeting_id = %s AND resolved = FALSE""",
                    (meeting_id,))
        errors = cur.fetchall()
    except Exception as e:
        logger.warning(e)
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

    if article is None:
         abort(404)

    # sort errors by date
    for error in errors:
        error["submitted_at"] = error["submitted_at"].strftime("%Y-%m-%d")

    sorted_errors = sorted(errors, key=lambda item: item['submitted_at'], reverse=True)

    return render_template("edit_article.html", article=article, errors=sorted_errors)