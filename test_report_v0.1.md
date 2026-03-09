## v0.1 Test Report
```bash
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.0.2, pluggy-1.6.0 -- /home/mike/myprojects/whatsupinwindsor/.venv/bin/python3
cachedir: .pytest_cache
metadata: {'Python': '3.10.12', 'Platform': 'Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.35', 'Packages': {'pytest': '9.0.2', 'pluggy': '1.6.0'}, 'Plugins': {'html': '4.2.0', 'metadata': '3.1.1'}}
rootdir: /home/mike/myprojects/whatsupinwindsor
configfile: pyproject.toml
testpaths: tests
plugins: html-4.2.0, metadata-3.1.1
collecting ... collected 14 items

tests/test_error_handling.py::test_non_200_response PASSED               [  7%]
tests/test_error_handling.py::test_timeout_handled PASSED                [ 14%]
tests/test_error_handling.py::test_missing_state_file PASSED             [ 21%]
tests/test_parsing.py::test_bad_entries_handled PASSED                   [ 28%]
tests/test_parsing.py::test_required_fields_present PASSED               [ 35%]
tests/test_parsing.py::test_date_parsing_valid PASSED                    [ 42%]
tests/test_parsing.py::test_classify_body PASSED                         [ 50%]
tests/test_state_logic.py::test_304_no_changes PASSED                    [ 57%]
tests/test_state_logic.py::test_first_run_creates_files PASSED           [ 64%]
tests/test_state_logic.py::test_modified_header_updates_state PASSED     [ 71%]
tests/test_state_logic.py::test_idempotent_double_run PASSED             [ 78%]
tests/test_state_logic.py::test_assignment_state_handler PASSED          [ 85%]
tests/test_state_logic.py::test_update_status_helper PASSED              [ 92%]
tests/test_state_logic.py::test_sort_then_assign PASSED                  [100%]

============================== 14 passed in 0.09s ==============================
```