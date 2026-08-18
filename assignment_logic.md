# Logic Chain for Assignment Status

>*Need a reliable way to keep track of status at document, assignment, and run level*

## Document Level
These statuses are reported by document-level operations in fetch_documents() and write_article()

### State Definition
**Status**|**Description**|**Action**
----------|---------------|----------
SUCCESS|Document was successfully fetched or summarized|Count towards available/summarized tally
RETRY|Document is available but something failed during fetch/summary|Count towards available but not complete. Drives STATUS_PARTIAL
FAIL|Document unreadable or not available|Remove from documents available tally

### State Transition: fetch_documents()
Current State|Event|New State
-------------|-----|---------
None|no url available for doc_type|RETRY
None|pdf url returns !=200|FAIL
None|returns document text dict|SUCCESS

>*Note: the above status belongs at the individual document level. If the entire materials url returns !=200, then that is STATUS_FAILED at the assignment level*

### State Transition: write_article()/review_article()
Current State|Event|New State
-------------|-----|---------
None|AI provider fails with exception|RETRY
None|The returned article json is missing keys|RETRY
None|The returned article has the wrong format|RETRY
None|The article is successfully summarized|SUCCESS


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



