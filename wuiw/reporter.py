# Module to create reporting bot
import requests
import io
import time
from pypdf import PdfReader
from bs4 import BeautifulSoup
from logging import getLogger
from wuiw.util import classify
from wuiw.config import HEADERS, STATUS_FOLLOW_UP, STATUS_SOURCED, STATUS_ASSIGNED, STATUS_PARTIAL, REQUEST_DELAY
from wuiw.log import civic_log
from datetime import datetime

SUPPORTED_DOCS = ["minutes", "agenda", "voting_grid"]

logger = getLogger(__name__)

def _transcribe_doc(pdf):
    reader = PdfReader(pdf)
    text = "".join(page.extract_text() for page in reader.pages)
    return text
  

def fetch_documents(url, doc_type=None):
    """Use beautiful soup to parse html for urls to pdf(s)
    
    Args:
        url (str): link to town documents
        doc_type (lis): specifies which type of docs to get

    Returns:
        documents (tup): tuple with items (documents list, status, error message)
    """
    response = requests.get(url, headers=HEADERS)
    civic_log.record(datetime.now(), url, response.status_code)
    time.sleep(REQUEST_DELAY)

    if response.status_code != 200:
        # If it can't fetch any documents because the materials packet link doesn't work, retry
        logger.warning(f"materials url returned {response.status_code}")
        return (None, STATUS_PARTIAL, f"assignment url returns {response.status_code}", 0)

    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('div', class_='item level1')
    print(f"found {len(items)} documents to parse")

    target_docs = {}
    for item in items:
        title = item.find('h1', class_='title').text.strip()
        detected_type = classify(title, town_id="windsorct", class_type="doc_type", fallback=True)
        href = item.find('a')['href']
        doc_url = href if href.startswith("http") else f"https://www.windsorct.gov{href}"
        target_docs[detected_type] = doc_url

    #Check target_docs.keys() against list of supported doc_types (from config.py) and count available documents
    available_documents = 0
    for key in target_docs.keys():
        if key in SUPPORTED_DOCS:
            available_documents += 1
    
    keys = [doc_type] if doc_type is not None else SUPPORTED_DOCS

    documents = []
    for key in keys:
        document = {}
        document["doc_type"] = key    
        if key not in target_docs:
            logger.warning(f"doc_type {key} not in materials")
            document["text"] = None
            document["status"] = STATUS_FOLLOW_UP
            document["error"] = f"doc_type {key} not in materials"
            documents.append(document)
            continue

        response_pdf = requests.get(target_docs[key], headers=HEADERS)
        civic_log.record(datetime.now(), target_docs[key], response_pdf.status_code)
        time.sleep(REQUEST_DELAY)

        if response_pdf.status_code != 200:
            logger.warning(f"No pdf returned for {key}; status: {response_pdf.status_code}")
            document["text"] = None
            document["status"] = STATUS_FOLLOW_UP
            document["error"] = f"No pdf returned for {key}; status: {response_pdf.status_code}"
            documents.append(document)
            continue

        pdf_stream = io.BytesIO(response_pdf.content)
        text = _transcribe_doc(pdf_stream)
        document["text"] = text
        document["status"] = STATUS_SOURCED
        document["error"] = None
        documents.append(document)

    # Review document statuses and set assignment status before returning
    stat = [d.get("status") for d in documents if "status" in d]
    if STATUS_FOLLOW_UP in stat:
        return (documents, STATUS_PARTIAL, None, available_documents)    

    return (documents, STATUS_ASSIGNED, None, available_documents)
   
def fetch_audio():
    pass
