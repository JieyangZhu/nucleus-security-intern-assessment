# Nucleus Security Software Engineering Intern Assessment

This repository contains my response to the two parts of the assessment:

1. [Python webhook code review](CODE_REVIEW.md)
2. A calculator web application with a Flask API and a browser interface

My answers to the coding challenge follow-up questions are in [FOLLOW_UP.md](FOLLOW_UP.md). The requested AI usage response is in `AI_USAGE.md`.

## Run the calculator

Python 3.10 or later is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in a browser.

## Run the tests

```bash
source .venv/bin/activate
pytest
```

## Implementation notes

- The browser sends each calculation to `POST /api/calculate` as JSON.
- The server accepts the four basic binary operators: `+`, `-`, `*`, and `/`.
- Arithmetic uses Python's `Decimal` type so common decimal calculations such as `0.1 + 0.2` produce the expected result.
- Inputs are parsed as decimal strings. The server does not evaluate input as source code.
- The API validates the JSON shape, operand format, operator, request size, and division by zero.
- The interface supports mouse, touch, and keyboard input and includes focus styles and accessible labels.

## API example

```bash
curl -X POST http://127.0.0.1:5000/api/calculate \
  -H 'Content-Type: application/json' \
  -d '{"left":"12.5","operator":"*","right":"4"}'
```

Expected response:

```json
{"result":"50"}
```

