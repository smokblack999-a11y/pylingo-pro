# PyLingo Pro security status

## Remote code execution

The HTTP endpoint `POST /api/run` is intentionally disabled and returns HTTP 410
(`CODE_EXECUTION_DISABLED`). The web process must never execute code supplied by
an unauthenticated browser request.

The editor UI remains available for lesson browsing and hint display. Code execution
and XP awards are disabled until a separate sandbox runner is implemented and tested.

## Requirements before re-enabling execution

- A dedicated, isolated worker (not the Flask web process).
- No host filesystem, environment, network, Docker socket, or repository credentials.
- CPU, memory, process-count, output-size, and wall-clock limits.
- Per-user authentication, authorization, quotas, and rate limits.
- Signed, single-use job requests bound to user, source hash, and expiry.
- Worker-produced signed results; browser-supplied PASS flags are never trusted.
- Regression tests for sandbox escape, timeouts, output exhaustion, and unauthorized access.

Do not expose this application publicly until authentication, TLS, and deployment
hardening are separately reviewed.
