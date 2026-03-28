# Module to create reporting bot
import requests
import io
import time
from pypdf import PdfReader
from bs4 import BeautifulSoup
from logging import getLogger
from wuiw.util import classify
from wuiw.config import DOCUMENT_TYPES, HEADERS, STATUS_ASSIGNED, STATUS_FAILED, REQUEST_DELAY

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
    time.sleep(REQUEST_DELAY)

    if response.status_code != 200:
        logger.warning(f"materials url returned {response.status_code}")
        return ({}, STATUS_FAILED, f"materials get returned {response.status_code}")

    documents = {}
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('div', class_='item level1')
    print(f"found {len(items)} documents to parse")

    target_docs = {}
    for item in items:
        title = item.find('h1', class_='title').text.strip()
        detected_type = classify(title, DOCUMENT_TYPES)
        # doc_url = f"https://www.windsorct.gov{item.find('a')['href']}" # TODO put this back when live
        doc_url = item.find('a')['href']
        target_docs[detected_type] = doc_url
    
    keys = [doc_type] if doc_type is not None else target_docs.keys()

    for key in keys:
        if key not in target_docs:
            logger.warning(f"doc_type {key} not in materials")
            continue

        response_pdf = requests.get(target_docs[key], headers=HEADERS)
        time.sleep(REQUEST_DELAY)

        if response_pdf.status_code != 200:
            logger.warning(f"No pdf returned for {key}; status: {response_pdf.status_code}")
            continue

        pdf_stream = io.BytesIO(response_pdf.content)
        text = _transcribe_doc(pdf_stream)
        documents[key] = text

    return (documents, STATUS_ASSIGNED, None)
   
def fetch_audio():
    pass
