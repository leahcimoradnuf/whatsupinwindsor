# Logic Chain for Assignment Status

>*Need a reliable way to keep track of status at document, assignment, and run level*

## Document Level
These statuses are reported by document-level operations in fetch_documents() and write_article(). Each operation returns a certain set of states related to the stage of the operation: fetch or write.

### State Definition: fetch_documents()
**Status**|**Description**
----------|---------------
SOURCED|Document was successfully fetched 
FOLLOW_UP|Document is available but something failed during fetch/summary
DEAD_LEAD|Document unreadable or not available

### State Transition: fetch_documents()
Current State|Event|New State
-------------|-----|---------
None|no url available for doc_type|FOLLOW_UP
None|pdf url returns !=200|DEAD_LEAD
None|pdf fetched, but empty|FOLLOW_UP
None|returns document text dict|SOURCED
FOLLOW_UP|retry() successfully fetches|SOURCED
FOLLOW_UP|retry() fails, under threshold|FOLLOW_UP
FOLLOW_UP|retry() threshold met|DEAD_LEAD

>*Note: the above status belongs at the individual document level. If the entire materials url returns !=200, then that is STATUS_FAILED at the assignment level*

**Data Shape Returned by fetch_documents()**

In v1.0 it is currently:
```python
documents = {"minutes": "minutes transcription", "agenda": "agenda transcription"}
```
The signature needs to change to include the fetch status code:
```python
documents = [{"doc_type": "minutes", "text": None, "status": "FOLLOW_UP", "error": "pdf url !=200"}, 
    {"doc_type": "agenda", "text": "agenda transcription", "status": "SOURCED", "error": None}]

# some logic to derive assignment level status from doc statuses here

return documents, status, error, count
```
Meaning fetch_documents() will return a list now instead of a dictionary, so main.py needs to handle that.

### State Definition: write_article()
Status|Description
------|-----------
REPORTING|The assignment exists and the writer is waiting for the reporter to fetch documents
DRAFT|The writer could not successfully produce an article, retry
DONE|Article is successfully written
ZERO|Article can't be delivered and manual intervention is needed

### State Transition: write_article()
Current State|Event|New State
-------------|-----|---------
REPORTING|AI provider fails with exception|DRAFT
REPORTING|The returned article json is missing keys|DRAFT
REPORTING|The returned article has the wrong format|DRAFT
REPORTING|The article is successfully summarized|DONE
DRAFT|retry() successfully summarizes|DONE
DRAFT|retry() fails, under threshold|DRAFT
DRAFT|retry() threshold met|ZERO

**Data Shape Returned by write_article()**

In v1.0 it is currently:
```python
return {
        "meeting_id": meeting_id,
        "meeting_date": article.get("meeting_date"),
        "byline": provider.model,
        "doc_type": doc_type,
        "summary": article
    }, STATUS_COMPLETE, None
```
Which can stay the same, the only thing that needs to change is the status taxonomy.

## Assignment Level
These statuses represent the current logic at all levels and need to be confined to the assignment level.

### State Definition
**Status**|**Description**|**Action**
----------|---------------|----------
STATUS_PENDING|The assignment has newly found documents to be assigned|pass to editor.assign()
STATUS_ASSIGNED|All available documents have been sent out for processing|pass to reporter.fetch_documents() and writer.write_article()
STATUS_COMPLETE|All available documents have been summarized successfully|pass summaries to editor.save_articles()
STATUS_PARTIAL|Some available documents have been summarized, others need to be checked and retried|Review and pass back to fetch_documents() or write_article() depending on case
STATUS_FAILED|No available documents were successfully summarized|Review logs, may require manual intervention

### State Transition
Current State|Event|New State
-------------|-----|---------
PENDING|assign() runs|ASSIGNED
ASSIGNED|all docs SOURCED|ASSIGNED
ASSIGNED|some SOURCED, some FOLLOW_UP|PARTIAL
ASSIGNED|all FOLLOW_UP|PARTIAL
ASSIGNED|all DEAD_LEAD|FAILED
ASSIGNED|some FOLLOW_UP, some DEAD_LEAD|PARTIAL
PARTIAL|some SOURCED, some DEAD_LEAD|WARNING
PARTIAL|retry succeeds, all SOURCED|ASSIGNED
PARTIAL|retry succeeds, some SOURCED, some DEAD_LEAD|WARNING
PARTIAL|retry fails, some SOURCED, some DEAD_LEAD|WARNING
PARTIAL|retry fails, all DEAD_LEAD|FAILED
ASSIGNED|all docs DONE|COMPLETE
ASSIGNED|some DONE, some DRAFT|PARTIAL
ASSIGNED|some DONE, some DRAFT, some ZERO|PARTIAL
ASSIGNED|some DONE, some ZERO|WARNING
ASSIGNED|some DRAFT, some ZERO|PARTIAL
ASSIGNED|all docs ZERO|FAILED
PARTIAL|retry succeeds (all now done)|COMPLETE
PARTIAL|retry still failing, under threshold|PARTIAL
PARTIAL|retry threshold exceeded for all documents|FAILED
PARTIAL|retry succeeds for some documents, others exceed threshold|WARNING
COMPLETE|audit finds new href|PARTIAL
FAILED|manual intervention|COMPLETE
WARNING|audit finds new href|PARTIAL

`editor.assign()` looks for new material to cover, STATUS_ASSIGNED.
`editor.retry()` looks for old material to re-check, STATUS_PARTIAL.
STATUS_COMPLETE, STATUS_FAILED, STATUS_WARNING require no automated action.

## Run Level



