# Module to create reporting bot
import requests
import io
import time
from pypdf import PdfReader
from bs4 import BeautifulSoup
from logging import getLogger
from wuiw.intake import classify
from wuiw.config import DOCUMENT_TYPES, HEADERS, STATUS_ASSIGNED, STATUS_FAILED

logger = getLogger(__name__)

def _transcribe_doc(pdf):
    """called by fetch_documents()"""
    reader = PdfReader(pdf)
    text = "".join(page.extract_text() for page in reader.pages)
    return text
  

def fetch_documents(url, doc_type=None):
    """Use beautiful soup to parse html for urls to pdf(s)
    url is link to materials page
    doc_type (list object or None) specifies which docs to return. Default None returns all doc types
    Returns dict object { doc_type: text }"""
    response = requests.get(url, headers=HEADERS)
    time.sleep(20)

    if response.status_code != 200:
        logger.warning(f"materials url returned {response.status_code}")
        return ({}, STATUS_FAILED, f"materials get returned {response.status_code}")

    documents = {}
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')

    for link in links:
        detected_type = classify(link.text, DOCUMENT_TYPES)
        response_pdf = requests.get(link['href'], headers=HEADERS)
        time.sleep(20)

        if response_pdf.status_code != 200:
            logger.warning(f"No pdf returned for {detected_type}; status: {response_pdf.status_code}")
            continue

        pdf_stream = io.BytesIO(response_pdf.content)
        text = _transcribe_doc(pdf_stream)
        documents[detected_type] = text

    if doc_type and doc_type in documents:
        return (documents[doc_type], STATUS_ASSIGNED, None)
    else:
        return (documents, STATUS_ASSIGNED, None)
   
   
def fetch_audio():
    pass
