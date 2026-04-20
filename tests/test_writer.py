from datetime import datetime
from wuiw.log import ai_log
from wuiw.writer import write_article

def test_v06_write_records_ai_request(mock_provider):
    ai_log.reset()
    ai_log.set_run_id(1)
    mock_provider.summarize.return_value = ({"article": "stuff"}, "OK", 100, 10)
    mock_provider.model = "claude-sonnet-4-6"
    
    response = write_article("town_council_1234_2026", "raw text", "minutes") # ai_log collects info within write article
    result = ai_log.info[0]
    # assertions on ai_log content
    assert result[0] == 1 # run_id
    assert isinstance(result[1], datetime)
    assert result[2] == "claude-sonnet-4-6"
    assert result[3] == "OK"
    assert result[4] == 100
    assert result[5] == 10
    ai_log.reset()