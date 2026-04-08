from datetime import datetime
from wuiw.log import ai_log, civic_log

def test_v06_valid_civic_log():
    civic_log.reset()
    civic_log.set_run_id(1)
    civic_log.record(datetime.now(), "http://link/to/something", 200)

    result= civic_log.info
    data = result[0]
    assert isinstance(result, list)
    assert isinstance(data, tuple)
    assert data[0] == 1
    assert isinstance(data[1], datetime)
    assert data[2] == "http://link/to/something"
    assert data[3] == 200

    # now add another row
    civic_log.record(datetime.now(), "http://link/to/another/thing/", 404)

    result= civic_log.info
    data = result[1]
    assert len(result) == 2
    assert isinstance(result, list)
    assert isinstance(data, tuple)
    assert data[0] == 1
    assert isinstance(data[1], datetime)
    assert data[2] == "http://link/to/another/thing/"
    assert data[3] == 404

    # now make sure everything clears properly
    civic_log.reset()

    assert civic_log.run_id is None
    assert civic_log.info == []

def test_v06_valid_ai_log():
    ai_log.reset()
    ai_log.set_run_id(1)
    ai_log.record(datetime.now(), "anthropic", 200, 9000, 500)

    result= ai_log.info
    data = result[0]
    assert isinstance(result, list)
    assert isinstance(data, tuple)
    assert data[0] == 1
    assert isinstance(data[1], datetime)
    assert data[2] == "anthropic"
    assert data[3] == 200
    assert data[4] == 9000
    assert data[5] == 500

    # add a row
    ai_log.record(datetime.now(), "openai", 200, 11000, 602)

    result= ai_log.info
    data = result[1]
    assert len(result) == 2
    assert isinstance(result, list)
    assert isinstance(data, tuple)
    assert data[0] == 1
    assert isinstance(data[1], datetime)
    assert data[2] == "openai"
    assert data[3] == 200
    assert data[4] == 11000
    assert data[5] == 602

    # now make sure everything clears properly
    ai_log.reset()

    assert ai_log.run_id is None
    assert ai_log.info == []

# Consider the case where run_id is None (hasn't been set)
def test_v06_invalid_run_id():
    civic_log.reset()
    civic_log.record(datetime.now(), "http://link/to/something", 200)

    ai_log.reset()
    ai_log.record(datetime.now(), "anthropic", 200, 9000, 500)

    result1= civic_log.info
    data1 = result1[0]
    assert isinstance(result1, list)
    assert data1[0] is None

    result2= ai_log.info
    data2 = result2[0]
    assert isinstance(result2, list)
    assert data2[0] is None


# Consider the case where run_id is an integer that isn't the run id... don't think i have to?