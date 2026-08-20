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

### State Definition: write_article()
**Status**|**Description**
----------|---------------
REPORTING|The assignment exists and the writer is waiting for the reporter to fetch documents
DRAFT|The writer could not successfully produce an article, retry
DONE|Article is successfully written
FAIL|Article can't be written and manual intervention is needed

### State Transition: write_article()
Current State|Event|New State
-------------|-----|---------
REPORTING|AI provider fails with exception|DRAFT
REPORTING|The returned article json is missing keys|DRAFT
REPORTING|The returned article has the wrong format|DRAFT
REPORTING|The article is successfully summarized|DONE
DRAFT|retry() successfully summarizes|DONE
DRAFT|retry() fails, under threshold|DRAFT
DRAFT|retry() threshold met|FAIL


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
ASSIGNED|all docs SUCCESS|COMPLETE
ASSIGNED|some SUCCESS, some RETRY|PARTIAL
ASSIGNED|some SUCCESS, some RETRY, some FAIL|PARTIAL
ASSIGNED|some SUCCESS, some FAIL|WARNING
ASSIGNED|some RETRY, some FAIL|PARTIAL
ASSIGNED|all docs FAIL|FAILED
PARTIAL|retry succeeds (all now done)|COMPLETE
PARTIAL|retry still failing, under threshold|PARTIAL
PARTIAL|retry threshold exceeded for all documents|FAILED
PARTIAL|retry succeeds for some documents, others exceed threshold|WARNING
COMPLETE|audit finds new href|PARTIAL
FAILED|manual intervention|COMPLETE
WARNING|audit finds new href|PARTIAL

## Run Level



