# ActivePrime QA automation assessment

Automated checks for the mock data-quality application. The tests use the Playwright sync API and pytest. Each test opens `http://localhost:8080/index.html` on its own.

The files in `app/` are the assessment application and are not modified.

## Setup

Use Python 3.11 or newer.

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Run

From the repository root, with the virtual environment activated:

```bash
pytest
```

pytest serves `app/` at `http://localhost:8080` for the session. Port 8080 needs to be free.

Run one test:

```bash
pytest tests/test_data_issues.py::test_checkbox_selection_counter
```

## What is covered

1. Open Data Issues and check that 10 issue cards are shown.
2. Read the original row of every card and check that its sfid is not empty.
3. On the 7th card, choose the original issue value and check that the final row updates to it.
4. On sfid `00Qak00000RHtuzEAD`, clear the final issue value, enter `123 Test Street`, confirm, and check the final row.
5. Select the 1st, 3rd, and 5th cards and check the counter reads `3 issue(s) selected`. Select all and check `10 issue(s) selected`. Clear the selection and check that the counter is hidden.
