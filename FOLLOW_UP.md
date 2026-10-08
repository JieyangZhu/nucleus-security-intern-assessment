# Part 2: Coding Challenge Follow-up

## 1. How far did you get?

I completed a working calculator with a responsive browser interface and a Flask backend. It supports addition, subtraction, multiplication, and division using mouse, touch, or keyboard input.

The backend exposes a JSON endpoint and performs the calculation with `Decimal`. It validates the request content type and shape, operand syntax and length, supported operators, request size, and division by zero. Results and errors are returned as JSON. The interface displays API errors without reloading the page and prevents duplicate requests while a calculation is in progress.

I also added unit tests for the arithmetic module and integration tests for the page and API, including malformed input and request-size cases.

## 2. What challenges did you face?

The main design choice was deciding where calculation should happen. A browser-only solution would be shorter, but the prompt allows backend logic and I wanted the submission to demonstrate a small, testable request boundary. I kept the arithmetic in a standalone Python module so it can be tested without Flask, while the route is responsible only for HTTP validation and response formatting.

Decimal input also needed a deliberate policy. JavaScript and Python binary floating-point arithmetic can display surprising results for inputs such as `0.1 + 0.2`. The API therefore accepts decimal strings and uses Python's `Decimal` type. It accepts ordinary signed decimal notation and deliberately rejects exponent notation, non-numeric values, unsupported operators, and overly long operands.

On the client, the awkward cases were calculator state transitions: entering a decimal point, replacing the display after an operator or result, changing the selected operator before evaluation, deleting digits, and handling an API failure without losing the current expression. I kept that state explicit in one object and routed pointer and keyboard input through the same functions.

## 3. What would you add with unlimited time?

I would add chained-operation semantics with a clear precedence model, a sign toggle, percentage operations, calculation history, and locale-aware number display. I would also add browser-level tests for keyboard navigation, focus behavior, small-screen layout, and the full request flow.

For a production deployment, I would add structured request logging and correlation IDs, rate limiting at the edge, security headers, automated dependency checks, a production WSGI server, and CI that runs the Python and browser tests. I would define a product limit for precision and result size rather than relying only on the current operand and decimal-context limits.

## 4. AI usage

See `AI_USAGE.md`.

## Questions and thoughts on the exercise

The two parts complement each other well: the review exercise tests how I reason about an existing boundary with security and reliability risks, while the calculator tests how I turn a small requirement into a working, testable application.

For the webhook task, I would want to confirm the vendor's exact signature encoding, retry behavior, event identifier, and role-mapping rules before approving an implementation. Those contract details determine the correct signature verification and idempotency design. For the calculator, I treated the four basic arithmetic operations as the required scope and documented the additional features I would consider separately rather than expanding the exercise without a product requirement.
