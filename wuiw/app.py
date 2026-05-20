import psycopg2
import psycopg2.extras
import os
import logging
from flask import Flask, render_template, abort, redirect, url_for, send_from_directory
from flask import request, session
from wuiw.config import get_db_connection
from wuiw.editor import update_article, report_error, approve_article, publish_article
from wuiw.main import main
from functools import wraps

# Initiate stuff
app = Flask(__name__)
logger = logging.getLogger(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

_run_in_progress = False

SITE_DIR = os.path.join(os.path.dirname(__file__), '..', 'site')

@app.errorhandler(404)
def page_not_found(error):
    # Renders 'not_available.html' and ensures the response code is 404
    return render_template('not_available.html'), 404

@app.route("/docs/")
@app.route("/docs/<path:subpath>")
def docs(subpath="index.html"):
    if subpath.endswith("/"):
        subpath = f"{subpath}index.html"
    return send_from_directory(SITE_DIR, subpath)

@app.route("/")
def index():
    if session.get('admin'):
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
                    WHERE articles.doc_type = 'minutes'""")
        articles = cur.fetchall()
        cur.close()
        conn.close()
        for article in articles:
            article["meeting_date"] = article["meeting_date"].strftime("%Y-%m-%d")

        sorted_articles = sorted(articles, key=lambda item: item['meeting_date'], reverse=True)
    else:
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
    if session.get('admin'):
        conn = get_db_connection() 
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
        cur.execute("""
                    SELECT
                        assignments.meeting_type,
                        assignments.materials,
                        assignments.reviewed,
                        assignments.published,
                        articles.meeting_id,
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
    else:
        conn = get_db_connection() 
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
        cur.execute("""
                    SELECT
                        assignments.meeting_type,
                        assignments.materials,
                        assignments.reviewed,
                        assignments.published,
                        articles.meeting_id,
                        articles.meeting_date,
                        articles.byline,
                        articles.summary
                    FROM assignments
                    JOIN articles ON assignments.meeting_id = articles.meeting_id
                    WHERE assignments.meeting_id = %s 
                    AND articles.doc_type = 'minutes'
                    AND assignments.published = TRUE;
            """, (meeting_id,))
        article = cur.fetchone()
        cur.close()
        conn.close()
        
    if article is None:
         abort(404)
    
    return render_template("article.html", article=article)

@app.route("/report-error", methods=['GET', 'POST'])
def report_error_route():
    if request.method == 'POST':
        meeting_id = request.form.get('meeting_id')
        text = request.form.get('feedback')
        report_error(meeting_id, text)
        return render_template("thanks_for_feedback.html")
    
    meeting_id = request.args.get('meeting_id')
    return render_template("report_error.html", meeting_id=meeting_id)

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
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('admin_login'))
    
    return render_template("/admin_login.html")

@app.route("/logout")
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for("index"))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login', next=request.url))
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
        cur.execute("""SELECT 
                        assignments.meeting_id,
                        assignments.meeting_type,
                        assignments.reviewed,
                        assignments.published,
                        COUNT(error_reports.id) as error_count
                    FROM assignments
                    LEFT JOIN error_reports 
                        ON assignments.meeting_id = error_reports.meeting_id
                        AND error_reports.resolved = FALSE
                    GROUP BY assignments.meeting_id, assignments.meeting_type, 
                            assignments.reviewed, assignments.published
                    HAVING COUNT(error_reports.id) > 0 
                        OR assignments.reviewed = FALSE 
                        OR assignments.published = FALSE""")
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

@app.route("/admin/run", methods=["POST"])
@login_required
def admin_run():
    global _run_in_progress
    if _run_in_progress:
        return redirect(url_for('admin_dashboard'))
    _run_in_progress = True
    # kick off background thread
    try:
        main()
    except Exception as e:
        logger.warning(e)
    finally:
        _run_in_progress = False
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/articles/<meeting_id>", methods=["GET", "POST"])
@login_required
def admin_article(meeting_id):
    if request.method == 'POST':
        print("POST received")
        print(request.form)
        items = []
        headline = request.form.get('headline')
        meeting_type = request.form.get('meeting_type')
        date = request.form.get('date')
        bullets = [b for b in request.form.getlist('bullets') if b.strip()]
        blurb = request.form.get('blurb')

        updates = {
            "assignment": {"meeting_type": meeting_type},
            "article": {
                "agenda": {"items": items},
                "minutes": {
                    "headline": headline,
                    "meeting_date": date,
                    "bullets": bullets,
                    "blurb": blurb
                }
            }
        }

        if request.form.get('action') == 'resolve': 
            update_article(meeting_id, updates, resolved=True)
        else:
            update_article(meeting_id, updates)
        
        return redirect(url_for('admin_dashboard'))

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

    return render_template("edit_article.html", meeting_id=meeting_id, article=article, errors=sorted_errors)

@app.route("/admin/articles/<meeting_id>/publish", methods=['POST'])
@login_required
def publish(meeting_id):
    publish = {"true": True, "false": False}
    publish_article(meeting_id, published=publish[request.form.get('published')])
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/articles/<meeting_id>/approve", methods=['POST'])
@login_required
def quick_approve(meeting_id):
    review = {"true": True, "false": False}
    approve_article(meeting_id, reviewed=review[request.form.get('reviewed')])
    return redirect(url_for('admin_dashboard'))
    