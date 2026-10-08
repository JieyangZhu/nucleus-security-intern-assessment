# AI Usage

## Disclosure and format

I used OpenAI Codex as a coding agent during this assessment. The agent could
read and edit files in the local repository, run terminal commands and tests,
inspect Git state, access the assessment Gist, and open the repository in VS
Code.

The prompts below have been lightly edited and grouped for readability
without changing their intent. They cover the substantive interactions that
affected the final repository; repeated repository-management instructions
have been condensed. AI outputs are summarized because most implementation
output was written directly to repository files rather than returned as a
single chat response. The resulting source files and documents are the
complete implementation artifacts.

I kept publication under my control. I instructed the agent not to commit or
push any changes without my permission. The agent also left the working-tree
files unstaged so that I could review them before publication.

---

# Requirement analysis

## Interaction 1: Reading and breaking down the requirements

### Prompt

> Read the GitHub Gist carefully and explain every requirement in the code
> review and coding challenge. Identify what must be implemented, what
> follow-up questions must be answered, and what must be delivered. Be
> precise and do not omit small requirements.

### What I wanted the AI to accomplish

I wanted a checklist of the assessment before deciding whether the repository
was complete. In particular, I wanted to distinguish the implementation
requirements from the written follow-up and delivery requirements.

### AI output

The agent divided the assessment into:

1. A review of either the PHP or Python webhook implementation.
2. Line-specific and general code-review comments.
3. AI usage follow-up questions for the review.
4. A calculator containing a frontend and any required backend logic.
5. Three general calculator follow-up questions and an additional AI usage
   question.
6. Delivery of the answers, questions or thoughts about the exercise, and a
   public GitHub repository link by email.

The agent also noted the suggested total time of approximately one hour and
that the assessment explicitly allowed AI use if it was disclosed.

### What the AI did well

The breakdown identified that a working calculator alone would not be a
complete response. The written follow-up questions, AI disclosure, exercise
notes, public repository, and email response were separate deliverables.

### What the AI did poorly

A requirements summary can still omit details or misstate the source. I did
not want the summary itself to become the source of truth.

### Did I re-prompt or change my approach?

Yes. Later in the process, I asked for a requirement-by-requirement audit
against the original Gist rather than relying only on this initial summary.

---

# Repository setup and implementation

## Interaction 2: Starting from a clean repository

### Prompt

> The new repository has been created. Start working on the assessment in the
> local repository and open it in VS Code. Do not create any commit or push
> anything without my permission. Leave the AI usage file empty because I
> will review and complete it separately.

### What I wanted the AI to accomplish

I wanted a complete local working draft while retaining control over Git
history and publication. Keeping the files uncommitted allowed me to inspect
the entire working tree before deciding what should be included remotely.

### AI output

The agent cloned the empty repository, opened it in VS Code, and confirmed
that the repository had no commits. It then created the assessment files only
in the local working tree and left `AI_USAGE.md` empty.

The implementation artifacts included:

- `CODE_REVIEW.md`;
- `FOLLOW_UP.md`;
- `README.md`;
- `calculator.py`;
- `app.py`;
- `templates/index.html`;
- `static/styles.css`;
- `static/app.js`;
- calculation and API tests;
- dependency and test configuration files.

### What the AI did well

The agent respected the repository boundary. It did not stage, commit, or
push any files, and it kept the AI disclosure separate from the initial
generated solution.

### What the AI did poorly

The instruction gave the agent broad implementation freedom. This made a
careful review of its architecture, code, and written answers necessary.

### Did I re-prompt or change my approach?

I retained the uncommitted workflow throughout the assessment and added
explicit testing and source-verification steps before publication.

---

## Interaction 3: Producing the webhook review and calculator

### Prompt

> Carefully answer every part of the assessment in the repository. Review the
> supplied Python webhook, provide accurate line-specific and general
> comments, and answer the non-AI follow-up questions. Build a complete
> calculator web application with a frontend and the backend logic needed for
> calculations. Keep the implementation small, testable, and well
> documented. Do not commit or push anything.

### What I wanted the AI to accomplish

I wanted the agent to prepare an initial end-to-end draft that I could inspect
as a single patch set. I expected the code review to focus on correctness,
security, reliability, and deployment concerns, and the calculator to have a
clear separation between interface, HTTP handling, and arithmetic logic.

### AI output: webhook review

The agent selected the Python implementation and created `CODE_REVIEW.md`.
The review covered:

- SQL injection in the two database operations;
- the difference between the claimed upsert and the actual insert;
- authorization of the externally supplied role;
- the insecure default webhook secret;
- exact-byte signature verification and constant-time comparison;
- JSON, content-type, type, field, length, and request-size validation;
- retry, replay, and idempotency considerations;
- transaction handling and connection cleanup;
- audit-data access and retention;
- SQLite and Flask development-server deployment concerns;
- suggested tests and questions for the service owner.

### AI output: calculator architecture

The agent implemented:

- a Flask JSON API;
- vanilla HTML, CSS, and JavaScript for the frontend;
- a standalone Python arithmetic module;
- decimal-string operands and Python `Decimal` arithmetic;
- an explicit allowlist for `+`, `-`, `*`, and `/`;
- controlled handling of division by zero;
- validation of the request content type, JSON shape, operands, operator, and
  request size;
- a responsive calculator interface;
- mouse, touch, and keyboard controls;
- accessible labels and focus styles.

The arithmetic code did not use `eval`. Separating `calculator.py` from the
Flask route allowed arithmetic behavior to be tested without running a web
server.

### AI output: tests and documentation

The agent created unit tests for arithmetic and integration tests for the
Flask page and API. The cases included normal operations, decimal arithmetic,
invalid operands, unsupported operators, malformed JSON, incorrect JSON
shapes, oversized requests, and division by zero.

It also documented environment setup, application startup, test execution,
implementation decisions, and an example API request in `README.md`.

### What the AI did well

The agent produced a cohesive implementation rather than unrelated snippets.
The arithmetic and HTTP boundaries were separated, inputs were explicitly
validated, and both successful and failing behavior were tested.

The use of decimal strings avoided converting browser input through binary
floating-point before reaching Python's `Decimal` type. This allowed common
calculations such as `0.1 + 0.2` to produce the expected decimal result.

### What the AI did poorly

The first client implementation cleared an API error during the final render
step, which could make the error disappear immediately after it was set. The
rendering and error-state logic had to be corrected.

The first pytest run also failed during test collection because the
repository root was not on pytest's import path in the local environment.

The initial code-review draft later proved to contain several factual details
that did not match the supplied snippet. Those problems were not detected by
the initial generation step.

### Did I re-prompt or change my approach?

Yes. I moved from requesting a complete draft to requiring separate automated
checks, live HTTP checks, and a final comparison against the source Gist and
code snippet.

---

# Testing and debugging

## Interaction 4: Running the verification checks

### Prompt

> Run the Python tests, a JavaScript syntax check, and Python compilation
> checks. If a check fails, report the failure, identify the smallest
> appropriate correction, apply it without weakening the tests, and rerun the
> checks. Also exercise the running HTTP application with a successful
> calculation and a division-by-zero request. Do not commit or push.

### What I wanted the AI to accomplish

I wanted failures to remain visible instead of allowing the implementation or
tests to be silently changed. I also wanted runtime evidence in addition to
source inspection.

### AI output

The first pytest attempt failed during collection with import errors for
`app` and `calculator`. The agent identified this as a pytest import-path
configuration problem and then added `pytest.ini`:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

After that correction, all 23 tests passed. The JavaScript syntax check and
Python compilation checks also passed.

The agent started the Flask application and verified:

- `GET /` returned `200 OK` with HTML;
- `12.5 * 4` returned `{"result":"50"}`;
- division by zero returned a controlled `400` JSON response;
- the page and API used appropriate content types.

The local development server was stopped after the checks.

### What the AI did well

The original pytest failure was reported rather than hidden. The correction
was made in repository-level test configuration and did not remove assertions
or weaken coverage.

The live HTTP checks exercised the main application path through a running
server rather than relying only on Flask's test client.

### What the AI did poorly

Passing unit, API, syntax, and HTTP checks did not verify every visual state
or browser interaction. They did not provide full end-to-end coverage of
keyboard navigation, focus behavior, responsive breakpoints, or every client
state transition.

### Did I re-prompt or change my approach?

I treated the automated and HTTP results as evidence for specific behavior,
not as proof that every aspect of the application was correct.

---

# Final requirement and accuracy audit

## Interaction 5: Checking whether the repository was complete

### Prompt

> Apart from the AI usage document, compare the current repository directly
> with the original GitHub Gist. Check every code-review requirement,
> calculator requirement, follow-up question, and delivery requirement. Also
> verify line numbers, schema names, algorithms, ports, test counts, and file
> references. Tell me whether anything is missing or inaccurate. Do not
> commit or push.

### What I wanted the AI to accomplish

I wanted a source-based audit rather than a general statement that the
application appeared complete. The agent had generated both the code and much
of the documentation, so I specifically asked it not to assume its earlier
statements were accurate.

### AI output

The audit found that the calculator and non-AI follow-up answers were
substantially complete, but identified several documentation issues:

1. A parameterized SQL example used an audit table and fields that did not
   match the supplied webhook code.
2. The review referred to port 5000 even though the supplied code used port
   8080.
3. An earlier signature recommendation introduced HMAC even though the
   exercise specified `SHA256(secret + body)`.
4. The repository did not clearly include the requested questions or thoughts
   about the exercise.

The agent corrected the code-review examples so they used the supplied
database schema, preserved the vendor's stated signature algorithm, and
referred to the correct server address and port. It also added a dedicated
questions-and-thoughts section to `FOLLOW_UP.md`.

The audit separately identified the remaining external delivery work: the
local files still needed final review, publication to the public repository,
and inclusion in the email response.

### What the AI did well

The audit found factual mismatches that broad proofreading had missed. It
also separated repository content from external delivery steps.

### What the AI did poorly

The agent had generated several of the errors that it later identified. Its
self-review was useful as an additional check, but it was not independent
verification.

### Did I re-prompt or change my approach?

Yes. I required the corrections to be checked directly against the original
Gist and Python snippet instead of accepting conceptually reasonable but
source-inaccurate examples.

---

# Overall evaluation

## What the AI did well

The coding agent was effective at:

- turning the assessment requirements into a working repository;
- identifying a broad range of webhook security and reliability concerns;
- separating arithmetic from HTTP handling;
- implementing explicit input validation;
- generating normal and failure-path tests;
- running tools and reporting failures;
- performing live HTTP checks;
- comparing the final repository against a structured requirements list.

Direct repository and terminal access reduced the gap between a textual
suggestion and an implementation that could be executed and inspected.

## What the AI did poorly

The agent sometimes:

- introduced identifiers that did not match the source material;
- suggested a familiar security pattern without preserving the supplied
  protocol;
- generated prose that required review for accuracy and tone;
- treated automated checks as stronger evidence than they were;
- failed to catch its own factual errors until a source-based audit was
  requested.

The main weakness was precision. Broad technical findings were often useful,
but line references, schema names, configuration values, and protocol details
still required comparison with the source.

## How my prompting approach changed

My earlier instructions were broad and focused on producing a complete draft.
Later instructions became more constrained and evidence-oriented. I added:

- an explicit source of truth;
- algorithms and schemas that must be preserved;
- actions the agent was prohibited from taking;
- concrete verification commands and cases;
- a distinction between confirmed defects and assumptions;
- a requirement to report failures before applying corrections;
- a final source-to-source audit.

This made the outputs easier to evaluate and reduced unsupported changes.

---

# Final review responsibility

Before submitting the repository, I will personally confirm that I can
explain:

- why direct SQL interpolation is unsafe;
- why the signature should be calculated over the exact request bytes;
- why constant-time comparison is appropriate;
- why webhook authentication does not automatically authorize an external
  role;
- how idempotency differs from an upsert;
- why the calculator sends operands as strings;
- why Python `Decimal` is used;
- how the API validates request content and structure;
- how division by zero and other invalid inputs are handled;
- how the browser state changes after an operator, result, deletion, or API
  error;
- what each automated test demonstrates;
- which delivery steps occur outside the repository.

The final repository contents and technical decisions remain my
responsibility. AI assistance accelerated analysis, implementation, and
verification, but it did not remove the need to understand, test, and defend
the submitted work.
