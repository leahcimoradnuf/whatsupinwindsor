import json
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, abort
from wuiw.config import get_db_connection

app = Flask(__name__)

@app.route("/home")
@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""SELECT 
                    assignments.meeting_id,
                    assignments.meeting_type,
                    assignments.materials,
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
    return render_template("index.html", articles=sorted_articles)

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
    abort(404)

@app.route("/support")
def support():
    abort(404)