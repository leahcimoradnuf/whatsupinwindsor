from flask import Flask, render_template, abort

app = Flask(__name__)

@app.route("/")
def index():
    # render chronological list of all articles

@app.route("/article/<meeting_id>")
def article(meeting_id):
    # render single article