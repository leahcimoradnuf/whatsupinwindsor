import os
import pytest
from wuiw.config import get_provider
from wuiw.journalist import _build_prompts
from unittest.mock import patch, MagicMock

def test_v06_anthropic_token_count(mock_anthropic_client, seeded_db):
    with patch.dict(os.environ, {"PROVIDER": "Anthropic"}):
        provider = get_provider()
        text = "summarize me"
        result = provider.summarize(text, "minutes")
    # assert result is (article, "OK", 100, 10)
    assert isinstance(result[0], dict)
    assert result[1] == "OK"
    assert result[2] == 100
    assert result[3] == 10

@pytest.mark.skip(reason="not developing openai client now")
def test_v06_openai_token_count(mock_openai_client):
    with patch.dict(os.environ, {"PROVIDER": "OpenAI"}):
        provider = get_provider()
        text = "summarize me"
        result = provider.summarize(text, "minutes")
    # assert result is (article, "OK", 100, 10)
    assert isinstance(result[0], dict)
    assert result[1] == "OK"
    assert result[2] == 100
    assert result[3] == 10

def test_v06_anthropic_fail(seeded_db):
    with patch("wuiw.journalist.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.usage.input_tokens = None
        mock_response.usage.output_tokens = None
        mock_response.content[0].text = None
        mock_client.messages.create.return_value = mock_response
        mock_client.messages.create.side_effect = Exception("API error")
        with patch.dict(os.environ, {"PROVIDER": "Anthropic"}):
            provider = get_provider()
            text = "summarize me"
            result = provider.summarize(text, "minutes")
        
        assert result[0] is None
        assert result[1] == "FAIL"
        assert result[2] is None
        assert result[3] is None

def test_v09_build_prompts(seeded_db):
    system, examples = _build_prompts("minutes")
    assert system !=0
    assert examples !=0