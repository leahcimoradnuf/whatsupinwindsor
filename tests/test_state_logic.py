

from unittest.mock import patch, MagicMock
from wuiw.intake import get_rss


def test_v01_304_no_changes():
    """if the Last-Modified header of the feed is not newer than the last run, do nothing"""
    mock_feed = MagicMock()
    mock_feed.status = 304

    with patch("wuiw.intake.feedparser.parse", return_value=mock_feed):

        result = get_rss("http://example.com/rss")

    assert result == {} # TODO decide if this should be deprecated
