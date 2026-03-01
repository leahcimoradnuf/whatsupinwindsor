

import os
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
from wuiw.intake import get_rss

load_dotenv()
def test_get_rss():
    url = os.getenv("RSS_URL")
    entries = get_rss(url)
    assert isinstance(entries, dict)

def test_get_rss_304_returns_empty():
    mock_feed = MagicMock()
    mock_feed.status = 304

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed), \
         patch("wuiw.intake.load_modified", return_value=None), \
         patch("wuiw.intake.save_modified") as mock_save:

        result = get_rss("http://example.com/rss")

    assert result == {}
    mock_save.assert_not_called()

