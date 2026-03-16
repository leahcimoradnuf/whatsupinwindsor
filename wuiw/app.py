import json
from flask import Flask, render_template, abort
from wuiw.config import ARTICLES_FILE

app = Flask(__name__)

@app.route("/home")
@app.route("/")
def index():
    with open(ARTICLES_FILE, 'r') as f:
        articles = json.load(f)
    sorted_articles = dict(sorted(articles.items(), key=lambda item: item[1]['meeting_date'], reverse=True))
    return render_template("index.html", articles=sorted_articles)

@app.route("/articles/<meeting_id>")
def article(meeting_id):
    # render single article
    with open(ARTICLES_FILE, 'r') as f:
        articles = json.load(f)
    if meeting_id not in articles:
        abort(404)
    return render_template("article.html", article=articles[meeting_id])

@app.route("/report-error")
def report_error():
    return render_template("report_error.html")

@app.route("/about")
def about():
    abort(404)

@app.route("/support")
def support():
    abort(404)