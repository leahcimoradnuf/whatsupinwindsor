#!/home/mike/myprojects/whatsupinwindsor/.venv/bin/python

import os
from dotenv import load_dotenv

from wuiw.intake import get_rss

load_dotenv()
def test_get_rss():
    url = os.getenv("RSS_URL")
    entries = get_rss(url)
    assert isinstance(entries, dict)

