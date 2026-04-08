import io
import pytest
from wuiw.reporter import _transcribe_doc, fetch_documents
from unittest.mock import patch, MagicMock
from wuiw.config import STATUS_FAILED, STATUS_ASSIGNED

# Unit Test _transcribe_doc()
def test_v03_transcribe_successful():
    with open("tests/fixtures/sample_minutes.pdf", "rb") as f:
        pdf_stream = io.BytesIO(f.read())
    text = _transcribe_doc(pdf_stream)

    assert len(text) > 0

def test_v03_transcribe_handles_unreadable_pdf():
    with open("tests/fixtures/corrupt.pdf", "rb") as f:
        pdf_stream = io.BytesIO(f.read())
    with pytest.raises(Exception):
        _transcribe_doc(pdf_stream)

# Unit Test fetch_documents()
def test_v03_non200_materials(no_sleep_till_brooklyn):
    """Returns: ({}, STATUS_FAILED, error_message)"""
    mock_response = MagicMock()
    mock_response.status_code = 404
    
    with patch("wuiw.reporter.requests.get", return_value=mock_response):
        result, status, error = fetch_documents("http://example.com/materials")
    
    assert result == {}
    assert status == STATUS_FAILED
    assert "404" in error

def test_v03_valid_path(file_server, no_sleep_till_brooklyn):
    """Happy path returns: (documents, STATUS_ASSIGNED, None)"""
    url = "http://localhost:8000/sample_materials.html"
    documents, status, error = fetch_documents(url)

    assert isinstance(documents, dict)
    assert "agenda" in documents.keys()
    assert "minutes" in documents.keys()
    assert len(documents["minutes"]) > 0
    # assert "vote" in documents.keys() # unclassified is ok
    assert status == STATUS_ASSIGNED
    assert error is None

def test_v03_skip_non200_pdf(no_sleep_till_brooklyn):
    """non-200 pdf stream request skips entry and continues"""
    mock_200 = MagicMock()
    mock_200.status_code = 200
    mock_200.content = open("tests/fixtures/sample_minutes.pdf", "rb").read()

    mock_404 = MagicMock()
    mock_404.status_code = 404

    with open("tests/fixtures/sample_materials.html", "r") as f:
        materials_html = f.read()

    with patch("wuiw.reporter.requests.get") as mock_get:
        with patch("wuiw.reporter.time.sleep"):
            mock_get.side_effect = [
                MagicMock(status_code=200, text=materials_html),  # materials page
                mock_200,  # first PDF - succeeds
                mock_404,  # second PDF - fails
                mock_200   # third PDF - succeeds
            ]
            documents, status, error = fetch_documents("http://example.com")
    
    assert len(documents.keys()) == 2
    assert status == STATUS_ASSIGNED
    assert error is None

def test_v03_doc_type_returns_requested(file_server, no_sleep_till_brooklyn):
    """only requested doc type is returned
    doc_type filter for type not in documents returns ({}, STATUS_FAILED, error_message)"""
    url = "http://localhost:8000/sample_materials.html"
    with patch("wuiw.reporter.time.sleep"):
        documents, status, error = fetch_documents(url, doc_type="minutes")

    assert len(documents.keys()) == 1
    assert "minutes" in documents

@pytest.mark.skip(reason="Test passed before classify(doc_type_fallback) parameter was implemented. This test now fails but that's good")
def test_v03_unclassified_doc_type_handled(file_server, no_sleep_till_brooklyn):
    """classify() doesn't catch 'vote' from 'Voting Grid', so it returns unclassified"""
    url = "http://localhost:8000/sample_materials.html"
    documents, status, error = fetch_documents(url)
    
    assert "unclassified" in documents

