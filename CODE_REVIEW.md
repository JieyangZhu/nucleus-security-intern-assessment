# Part 1: Python Webhook Code Review

## Summary

The endpoint has several issues that should be fixed before it is exposed to webhook traffic. The highest priority problems are SQL injection, trusting an externally supplied role, and a signature check whose correctness depends on applying the vendor's hashing contract to the exact request bytes. The handler also needs clearer validation, replay protection, database lifecycle management, and production deployment configuration.

## Line-specific comments

### Lines 41–48: SQL injection in both inserts

Both SQL statements interpolate values directly into the query. `raw`, `email`, and `role` come from the request and can alter the SQL. Quoting the value in the f-string does not make it safe.

Use placeholders and pass the values separately:

```python
cur.execute(
    "INSERT INTO webhook_audit (email, raw_json) VALUES (?, ?)",
    (email, raw.decode("utf-8")),
)
cur.execute(
    "INSERT INTO users (email, role) VALUES (?, ?)",
    (email, role),
)
```

Parameterized queries are required even after application-level validation.

### Lines 45–48: The comment says "upsert", but the code only inserts

Deliveries can be retried. A second delivery for the same user will either create a duplicate or fail, depending on the schema. Add a unique constraint for the natural identifier and state the conflict policy explicitly. For example, if email is the intended identifier:

```sql
INSERT INTO users (email, role)
VALUES (?, ?)
ON CONFLICT(email) DO UPDATE SET role = excluded.role;
```

Whether a retry should update an existing role is a product decision. A safer design may deduplicate by the provider's event ID and leave an existing account unchanged.

### Lines 34–35: The request controls an authorization-sensitive field

The code accepts any `role` supplied in the webhook body, including `admin`. A validly signed event only proves that the provider sent it; it does not prove that every value is allowed by this application.

Map provider events to a small allowlist of local roles and default to the least privileged role. Reject unknown values. The unused `metadata.source` field may be relevant to this policy, but it should also be validated rather than trusted.

### Lines 10 and 15–20: Signature verification is fragile

There are several separate problems:

- Falling back to `dev-secret` can silently run a deployed service with a known secret. Startup should fail when the secret is missing.
- The digest is calculated from `WEBHOOK_SECRET + raw.decode("utf-8")`. A webhook contract normally defines the exact bytes, algorithm, and signature encoding. Decoding and rebuilding the content can make verification differ from what the sender signed.
- `expected == sig` is not a constant-time comparison.
- The signature header format is not validated, so a prefix or version included by the provider would be handled incorrectly.

The comment says the vendor requires `SHA256(secret + body)`. That contract can be implemented over the original body bytes without decoding and re-encoding them:

```python
import hmac

expected = hashlib.sha256(
    WEBHOOK_SECRET.encode("utf-8") + raw_body
).hexdigest()

if not hmac.compare_digest(expected, supplied_signature):
    abort(401)
```

`hmac.compare_digest` is used here only for the constant-time comparison; this example preserves the vendor's stated concatenation algorithm. The final implementation should also follow the vendor's exact signature encoding and header format.

### Lines 24–35: The request has no structured validation

`json.loads` can raise on invalid JSON. Valid JSON can still be an array, a scalar, or an object with missing fields. `email` can be absent or the wrong type, and an unbounded body can consume excessive memory or storage.

Before using the payload:

- enforce `application/json` and a request-size limit;
- catch decoding failures and return a consistent `400` response;
- require an object with the documented fields;
- validate field types, lengths, and the email format;
- reject unsupported roles and event types;
- decide whether unknown fields are rejected or ignored.

Schema validation also makes the webhook contract testable and easier to evolve.

### Whole handler: Replay protection and idempotency are undefined

A captured valid request can be sent again because the signature authenticates content but does not establish freshness. Webhook providers also retry legitimate events after timeouts.

If the provider supplies a signed timestamp and event ID, verify that the timestamp is within an allowed window and store the event ID under a unique constraint in the same transaction as the business change. Repeated event IDs should return a successful idempotent response without applying the change again. If those fields are unavailable, the integration specification should define another deduplication key.

### Lines 37–50: Database cleanup and failure behavior need work

The connection is never closed. Exceptions during either insert or commit are not translated into a controlled response, and the rollback behavior is implicit. Under load this can leak resources; on failure it produces an unstructured `500` and may encourage retries without enough information to diagnose the cause.

Use Flask's application context to open one connection per request and close it in `teardown_appcontext`, or use a context manager. Wrap the related audit and user changes in one explicit transaction, roll back on failure, log an internal correlation or event ID, and return a small JSON error without database details.

SQLite also permits only limited concurrent writes. Confirm that its locking and durability behavior are acceptable for the expected webhook volume; otherwise use the application's production database.

### Lines 40–43: The audit record stores the full body without a data policy

The raw event may contain personal or future sensitive fields. Storing the entire payload increases the effect of a database disclosure and creates retention obligations. It also duplicates unbounded input.

Store the minimum fields needed for traceability, such as event ID, event type, outcome, and receipt time. If the raw payload is genuinely required, define access controls, encryption, size limits, redaction, and retention/deletion rules.

### Lines 9 and 54–55: The storage path and server are development defaults

`/tmp/app.db` can disappear between restarts and is not shared across multiple instances. `app.run(host="0.0.0.0", port=8080)` starts Flask's development server and listens on every network interface. Production deployment should use durable configuration for the database and a production WSGI server behind TLS. Debug mode must remain disabled.

## General comments

### Suggested processing order

1. Reject oversized requests before reading the body.
2. Read the raw body once.
3. Parse and validate the signature header, then verify it against those exact bytes.
4. Parse JSON and validate the event schema and authorization policy.
5. Check freshness and deduplicate the event in the database transaction.
6. Apply the user change and record a minimal audit entry atomically.
7. Return a consistent JSON response and log operational details using the event ID.

This order avoids doing business work before authentication and keeps a failed database transaction from recording only half of the intended state.

### Tests I would add

- a known valid signed payload and altered-body/altered-signature cases;
- missing, malformed, incorrectly encoded, and unsupported-version signature headers;
- missing secret at startup;
- invalid JSON, non-object JSON, missing fields, wrong types, excessive lengths, and an oversized body;
- SQL metacharacters in every string field to confirm values are stored literally;
- accepted and rejected role mappings, including an attempted `admin` role;
- duplicate event delivery and an expired signed timestamp;
- a forced failure between the two writes to confirm atomic rollback;
- concurrent delivery behavior at the expected traffic level;
- responses that do not expose stack traces, secrets, SQL, or personal data.

### Questions for the service owner

1. What exact signature algorithm, canonical byte sequence, header format, and key-rotation procedure does the sender specify?
2. Does the provider include a signed timestamp and globally unique event ID?
3. What delivery, retry, and ordering guarantees does the provider make?
4. Which event types and sources may create users, and how should external roles map to local permissions?
5. Should a repeated email update an existing user, be ignored, or be treated as a conflict?
6. What audit fields are required, who may access them, and how long should they be retained?
7. What request volume, latency target, and deployment topology should the database support?

## AI usage follow-up

See `AI_USAGE.md`.
