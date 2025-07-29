# Operational Guidelines

This document consolidates key operational aspects of the Fabric MCP Server, including coding standards, testing strategy, error handling, and security best practices.

## Coding Standards

These standards are mandatory for all code generation by AI agents and human developers. Deviations are not permitted unless explicitly approved and documented as an exception in this section or a linked addendum.

* **Primary Language & Runtime:** Python >=3.11 with CPython (as per Definitive Tech Stack Selections).
* **Style Guide & Linter:**
  * **Tools:** `Ruff` for formatting and primary linting, `Pylint` for additional static analysis, `isort` for import sorting (often managed via Ruff). `Pyright` for static type checking in strict mode.
  * **Configuration:**
    * Ruff: Configured via `.ruff.toml` and/or `pyproject.toml`.
    * Pylint: Configured via `.pylintrc`.
    * isort: Configured in `pyproject.toml` (often via `[tool.ruff.lint.isort]`).
    * Pyright: Configured in `pyproject.toml` (under `[tool.pyright]`) for strict mode.
  * **Enforcement:** Linter rules are mandatory and must be enforced by `pre-commit` hooks and CI checks.
* **Naming Conventions:**
  * Variables: `snake_case`
  * Functions/Methods: `snake_case`
  * Classes/Types/Interfaces: `PascalCase` (e.g., `MyClass`, `FabricPatternDetail`)
  * Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
  * Files: `snake_case.py` (e.g., `api_client.py`)
  * Modules/Packages: `snake_case` (e.g., `fabric_mcp`)
* **File Structure:** Adhere strictly to the layout defined in the "Project Structure" section of the main Architecture Document or `docs/project-structure.md`.
* **Unit Test File Organization:**
  * Location: Unit test files will be located in the `tests/unit/` directory, mirroring the `src/fabric_mcp/` package structure where appropriate.
  * Naming: Test files must be prefixed with `test_` (e.g., `test_api_client.py`, `test_core.py`). Test functions within these files must also be prefixed with `test_`.
* **Asynchronous Operations:**
  * Always use `async` and `await` for asynchronous I/O operations (e.g., `httpx` calls, FastMCP stream handling).
  * Ensure proper error handling for `async` operations, including `try...except` blocks for `async` calls.
* **Type Safety:**
  * **Type Hinting:** Comprehensive type hints are mandatory for all new functions, methods (including `self` and `cls` arguments), and variable declarations. Utilize Python's `typing` module extensively.
  * **Strict Mode:** `Pyright` (or MyPy if also used by linters) will be configured for strict type checking. All type errors reported must be resolved.
  * **Type Definitions:** Complex or shared type aliases and `TypedDict` definitions should be clearly defined, potentially in a dedicated `types.py` module within relevant packages if they are widely used, or co-located if specific to a module.
  * **Policy on `Any`:** Usage of `typing.Any` is strongly discouraged and requires explicit justification in comments if deemed absolutely necessary. Prefer more specific types like `object`, `Callable[..., T]`, or `TypeVar`.
* **Comments & Documentation:**
  * **Code Comments:** Explain *why*, not *what*, for complex or non-obvious logic. Avoid redundant comments. Use Python docstrings (Google or NumPy style preferred, to be consistent) for all public modules, classes, functions, and methods. Docstrings must describe purpose, arguments, return values, and any exceptions raised.
  * **READMEs:** Each significant module or component might have a brief README if its setup or usage is complex and not self-evident from its docstrings or the main project `README.md`.
* **Dependency Management:**
  * **Tool:** `uv` is used for package and environment management.
  * **Configuration:** Dependencies are defined in `pyproject.toml`. The `uv.lock` file ensures reproducible builds.
  * **Policy on Adding New Dependencies:** New dependencies should be carefully considered for their necessity, maintenance status, security, and license. They must be added to `pyproject.toml` with specific, pinned versions where possible, or using conservative version specifiers (e.g., `~=` for patch updates, `^=` for minor updates if strictly following SemVer and API stability is expected).
  * **Versioning Strategy:** Prefer pinned versions for all dependencies to ensure build reproducibility and avoid unexpected breaking changes, especially crucial for AI agent code generation.

### Detailed Language & Framework Conventions

#### Python Specifics

* **Immutability:**
  * Prefer immutable data structures where practical (e.g., use tuples instead of lists for sequences that should not change).
  * Be cautious with mutable default arguments in functions/methods; use `None` as a default and initialize mutable objects inside the function body if needed.
* **Functional vs. OOP:**
  * Employ classes for representing entities (like MCP tool request/response models if complex), services (like `FabricApiClient`), and managing state if necessary.
  * Use functions for stateless operations and utility tasks.
  * Utilize list comprehensions and generator expressions for concise and readable data transformations over `map` and `filter` where appropriate.
* **Error Handling Specifics (Python Exceptions):**
  * Always raise specific, custom exceptions inheriting from a base `FabricMCPError` (which itself inherits from `Exception`) for application-specific error conditions. This allows for cleaner `try...except` blocks. Example: `class FabricApiError(FabricMCPError): pass`.
  * Use `try...except...else...finally` blocks appropriately for robust error handling and resource cleanup.
  * Avoid broad `except Exception:` or bare `except:` clauses. If used, they must re-raise the exception or log detailed information and handle the situation specifically.
* **Resource Management:**
  * Always use `with` statements (context managers) for resources that need to be reliably closed or released, such as file operations (if any) or network connections managed by `httpx` if not handled by its higher-level client context management.
* **Type Hinting (Reiteration & Emphasis):**
  * All new functions and methods *must* have full type hints for all arguments (including `self`/`cls`) and return values.
  * Run `Pyright` in strict mode as part of CI/linting to enforce this.
* **Logging Specifics (Python `logging` module with `RichHandler`):**
  * Use the standard Python `logging` module, configured with `RichHandler` for console output to leverage `rich` formatting capabilities.
  * Acquire loggers via `logging.getLogger(__name__)`.
  * Log messages should provide context as outlined in the "Error Handling Strategy." Do not log sensitive information like API keys.
* **Framework Idioms:**
  * **Click:** Utilize decorators (`@click.command()`, `@click.option()`, `@click.argument()`) for defining CLI commands and options. Structure CLI logic clearly within command functions.
  * **FastMCP:** Follow FastMCP's patterns for registering tools and handling request/response cycles. If FastMCP provides specific hooks or extension points, they should be used as intended (potentially in the proposed `server_hooks.py`).
  * **httpx:** Use an `httpx.AsyncClient` instance, potentially as a singleton or managed context, for making calls to the Fabric API, especially for connection pooling and consistent configuration (headers, timeouts).
* **Key Library Usage Conventions:**
  * When using `httpx`, explicitly set connect and read timeouts for all requests to the Fabric API.
  * Ensure proper handling of `httpx.Response.raise_for_status()` or manual status code checking for API responses.
* **Code Generation Anti-Patterns to Avoid (for AI Agent Guidance):**
  * Avoid overly nested conditional logic (aim for a maximum of 2-3 levels; refactor complex conditions into separate functions or use other control flow patterns).
  * Avoid single-letter variable names unless they are trivial loop counters (e.g., `i`, `j`, `k` in simple loops) or very common idioms in a small, obvious scope.
  * Do not write code that bypasses the intended use of chosen libraries (e.g., manually constructing multipart form data if `httpx` can handle it).
  * Ensure all string formatting for user-facing messages or logs uses f-strings or the `logging` module's deferred formatting; avoid manual string concatenation with `+` for building messages.

## Overall Testing Strategy

This section outlines the project's comprehensive testing strategy, which all AI-generated and human-written code must adhere to. It complements the testing tools listed in the "Definitive Tech Stack Selections."

* **Tools:**

  * **Primary Testing Framework:** `Pytest`.
  * **Code Coverage:** `pytest-cov`.
  * **Mocking:** Python's built-in `unittest.mock` library.

* **Unit Tests:**

  * **Scope:** Test individual functions, methods, and classes within the `fabric_mcp` package in isolation. Focus will be on business logic within MCP tool implementations (`core.py`), utility functions (`utils.py`), CLI argument parsing (`cli.py`), API response parsing in `api_client.py`, and transport configurations (`server_transports.py`).
  * **Location & Naming:** As defined in "Coding Standards": located in `tests/unit/`, mirroring the `src/fabric_mcp/` structure, with filenames `test_*.py` and test functions prefixed with `test_`.
  * **Mocking/Stubbing:** All external dependencies, such as calls made by `httpx` within the `Fabric API Client`, file system operations (if any), and system time (if relevant for specific logic), MUST be mocked using `unittest.mock`.
  * **AI Agent Responsibility:** The AI Agent tasked with developing or modifying code MUST generate comprehensive unit tests covering all public methods/functions, significant logic paths (including conditional branches), common edge cases, and expected error conditions for the code they produce.

* **Integration Tests:**

  * **Scope:**
        1. **Internal Component Interaction:** Test the interaction between major internal components, primarily focusing on the flow from `MCP Tool Implementations (core.py)` to the `Fabric API Client (api_client.py)`. This involves verifying that MCP tool logic correctly invokes the API client and processes its responses (both success and error), with the actual Fabric API HTTP calls being mocked.
        2. **Live Fabric API Interaction:** Validate the Fabric MCP Server's interaction with a live (locally running) `fabric --serve` instance. These tests will cover the successful execution of each defined MCP tool against the live Fabric backend, verifying correct request formation to Fabric and response parsing from Fabric, including SSE stream handling.
  * **Location:** `tests/integration/`.
  * **Environment:** For tests requiring a live Fabric API, clear instructions will be provided (e.g., in a test-specific README or a contributing guide) on how to run `fabric --serve` locally with any necessary patterns or configurations for the tests to pass.
  * **AI Agent Responsibility:** The AI Agent may be tasked with generating integration tests for key MCP tool functionalities, especially those validating the interaction with the (mocked or live) Fabric API.

* **End-to-End (E2E) Tests:**

  * **Scope:** Simulate an MCP client interacting with the Fabric MCP Server across all supported transports (stdio, Streamable HTTP, SSE). These tests will cover common user workflows for each defined MCP tool, ensuring the entire system works as expected from the client's perspective through to the Fabric API (which might be mocked at its boundary for some E2E scenarios to ensure deterministic behavior, or live for full-stack validation).
  * **Tools:** This may involve creating a lightweight test MCP client script using Python (e.g., leveraging the `modelcontextprotocol` library directly) or using existing MCP client development tools if suitable for test automation.
  * **AI Agent Responsibility:** The AI Agent may be tasked with generating E2E test stubs or scripts based on user stories or BDD scenarios, focusing on critical happy paths and key error scenarios for each transport.

* **Test Coverage:**

  * **Target:** A minimum of 90% code coverage (line and branch where applicable) for unit tests, as measured by `pytest-cov`. While this is a quantitative target, the qualitative aspect of tests (testing meaningful behavior and edge cases) is paramount.
  * **Measurement:** Coverage reports will be generated using `pytest-cov` and checked as part of the CI process.

* **Mocking/Stubbing Strategy (General):**

  * Prefer using `unittest.mock.patch` or `MagicMock` for replacing dependencies.
  * Strive for tests that are fast, reliable, and isolated. Test doubles (stubs, fakes, mocks) should be used judiciously to achieve this isolation without making tests overly brittle to implementation details of mocked components.

* **Test Data Management:**

  * Test data (e.g., sample pattern names, mock API request/response payloads, MCP message structures) will primarily be managed using Pytest fixtures or defined as constants within the respective test modules.
  * For more complex data structures, consider using helper functions or small, local data files (e.g., JSON files in a test assets directory) loaded by fixtures.

## Error Handling Strategy

A robust error handling strategy is crucial for providing a reliable and user-friendly experience. This section outlines the approach for handling errors within the Fabric MCP Server.

* **General Approach:**

  * The primary mechanism for error handling within the Python application will be through exceptions. Custom exceptions may be defined for specific error conditions arising from the Fabric API client or core logic to allow for more granular error management.
  * Errors propagated to the MCP client will be formatted as standard MCP error objects, including a URN-style `type`, a `title`, and a `detail` message, as specified in the DX/Interaction document.
  * For CLI operations, errors will be clearly reported to `stderr`, potentially using `rich` for better formatting, and the server will exit with a non-zero status code for critical startup failures.

* **Logging:**

  * **Library/Method:** The `rich` library will be used for enhanced console output, and Python's standard `logging` module will be configured to work with it for structured logging.
  * **Format:** Logs should be structured (e.g., JSON format is preferred for production-like deployments if easily configurable, otherwise human-readable with clear timestamp, level, and message). For `rich`-based console output, a human-readable, color-coded format will be used.
  * **Levels:** Standard Python logging levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) will be used. The log level will be configurable via the `--log-level` CLI flag and the `FABRIC_MCP_LOG_LEVEL` environment variable.
  * **Context:** Logs for errors should include relevant contextual information such as:
    * Timestamp
    * Log level
    * Module/function where the error occurred
    * A unique request ID or correlation ID if feasible (especially for HTTP transports)
    * Sanitized key parameters related to the operation
    * The error message and potentially a stack trace for `DEBUG` level.

* **Specific Handling Patterns:**

  * **External API Calls (to `fabric --serve`):**
    * **HTTP Errors:** The `Fabric API Client` (`api_client.py`) will handle HTTP status codes from the Fabric API.
      * `4xx` errors (e.g., `401 Unauthorized`, `403 Forbidden`, `404 Not Found`) will be translated into specific MCP error types and logged appropriately. For instance, a `404` when fetching a pattern could become `urn:fabric-mcp:error:pattern-not-found`.
      * `5xx` server errors from Fabric will be treated as critical failures of the upstream service and result in an MCP error like `urn:fabric-mcp:error:fabric-api-unavailable` or `urn:fabric-mcp:error:fabric-internal-error`.
    * **Connection Errors:** Network issues (e.g., connection refused, timeouts) when calling the Fabric API will be caught by `httpx` and should result in an MCP error (e.g., `urn:fabric-mcp:error:fabric-api-unavailable`).
    * **Retries:** The `Fabric API Client` will use `httpx-retries` to automatically retry idempotent requests on transient network errors or specific server-side error codes (e.g., 502, 503, 504) as configured. Max retries and backoff strategy will be defined.
    * **Timeouts:** Explicit connect and read timeouts will be configured for `httpx` to prevent indefinite blocking.
    * **SSE Stream Errors:** If an error occurs *during* an active SSE stream from the Fabric API (e.g., Fabric sends an error event or the connection drops), the `Fabric API Client` will detect this. The MCP Tool Implementation for `fabric_run_pattern` will then terminate the MCP stream to the client and send a distinct MCP error object (e.g., `urn:fabric-mcp:error:fabric-stream-interrupted`).
  * **Internal Errors / Business Logic Exceptions:**
    * Unexpected errors within the Fabric MCP Server's core logic will be caught by a top-level error handler for each MCP tool invocation.
    * These will be logged with detailed stack traces (at `DEBUG` or `ERROR` level).
    * A generic MCP error (e.g., `urn:fabric-mcp:error:internal-server-error`) will be sent to the client to avoid exposing internal details, but with a unique identifier (correlation ID if implemented) that can be used to find the detailed log.
  * **MCP Request Validation Errors:**
    * If an MCP client sends a malformed request (e.g., missing required parameters, incorrect data types for parameters), the FastMCP library or the tool implementation layer should catch this.
    * An MCP error with a type like `urn:fabric-mcp:error:invalid-request` or `urn:mcp:error:validation` will be returned to the client with details about the validation failure.
  * **Configuration Errors:**
    * Missing or invalid essential configurations (e.g., unparseable `FABRIC_BASE_URL`) at startup will result in clear error messages logged to `stderr` and the server may fail to start.
  * **Transaction Management:** Not applicable, as the Fabric MCP Server is stateless. Data consistency is the responsibility of the `fabric --serve` instance.

## Security Best Practices

The following security considerations and practices are mandatory for the development and operation of the Fabric MCP Server.

* **Input Sanitization/Validation:**

  * All parameters received from MCP clients for MCP tool execution (e.g., `pattern_name`, `input_text`, `model_name` for `fabric_run_pattern`) MUST be validated by the respective tool implementation in `core.py` before being used or passed to the `Fabric API Client`.
  * Validation should check for expected types, formats (e.g., ensuring `pattern_name` is a string and does not contain malicious path traversal characters if used in constructing API paths, though `httpx` typically handles URL encoding), and reasonable length limits to prevent abuse or unexpected behavior.
  * The `click` framework provides some initial validation for CLI arguments.

* **Output Encoding:**

  * The primary output to MCP clients is structured JSON (for tool responses or MCP errors) or SSE data chunks (which are also JSON formatted as per Fabric's `StreamResponse`). The `FastMCP` library and standard JSON serialization libraries are expected to handle correct encoding, preventing injection issues into the MCP communication channel.
  * Data relayed from the Fabric API is assumed to be correctly formatted by Fabric; our server focuses on faithfully transmitting it within the MCP structure.

* **Secrets Management:**

  * The `FABRIC_API_KEY` is a critical secret and MUST be handled securely.
  * It MUST be provided to the server exclusively via the `FABRIC_API_KEY` environment variable.
  * The server MUST NEVER hardcode the `FABRIC_API_KEY` or include it directly in source control.
  * The `FABRIC_API_KEY` MUST NOT be logged in clear text. If logging API interactions for debugging, the key itself must be masked or omitted from logs.
  * The `api_client.py` will read this key from the environment via the Configuration Component and include it in the `X-API-Key` header for requests to the Fabric API.
  * The `fabric_get_configuration` MCP tool has a specific NFR to redact API keys (and other known sensitive values) received from the Fabric API `/config` endpoint before relaying them to the MCP client, using a placeholder like `"[REDACTED_BY_MCP_SERVER]"`.

* **Dependency Security:**

  * Project dependencies managed by `uv` via `pyproject.toml` and `uv.lock` should be regularly checked for known vulnerabilities.
  * Tools like `uv audit` (if available and analogous to `pip-audit` or `npm audit`) or other vulnerability scanners (e.g., Snyk, Dependabot alerts integrated with GitHub) should be used periodically or as part of the CI process.
  * Vulnerable dependencies, especially high or critical ones, must be updated promptly. New dependencies should be vetted before addition.

* **Authentication/Authorization:**

  * **To Fabric API:** The Fabric MCP Server authenticates to the Fabric REST API using the `FABRIC_API_KEY` if provided.
  * **MCP Client to Fabric MCP Server:** The MVP of the Fabric MCP Server does not define its own user authentication or authorization layer for incoming MCP client connections. Security for these connections relies on the inherent security of the chosen transport:
    * `stdio`: Assumes a secure local environment where the client process and server process are run by the same trusted user.
    * `http`/`sse`: For network-based transports, it's recommended to run the server behind a reverse proxy (e.g., Nginx, Caddy) that can enforce TLS (HTTPS), and potentially client certificate authentication or network-level access controls (firewalls, IP whitelisting) if needed by the deployment environment. These external measures are outside the direct scope of the `fabric-mcp` application code but are operational best practices.

* **Principle of Least Privilege (Implementation):**

  * The OS user account running the `fabric-mcp` server process should have only the necessary permissions required for its operation (e.g., execute Python, bind to a configured network port if using HTTP/SSE, read environment variables, make outbound network connections to the Fabric API).
  * It should not run with elevated (e.g., root) privileges unless absolutely necessary for a specific, justified reason (none anticipated).

* **API Security (for HTTP/SSE Transports):**

  * **HTTPS:** While the Python ASGI server (like Uvicorn, which FastMCP might use under the hood for HTTP transports) can serve HTTP directly, production deployments MUST use a reverse proxy to terminate TLS and serve over HTTPS.
  * **Standard HTTP Security Headers:** A reverse proxy should also be configured to add standard security headers like `Strict-Transport-Security` (HSTS), `Content-Security-Policy` (CSP) if serving any HTML content (not typical for this MCP server), `X-Content-Type-Options`, etc.
  * **Rate Limiting & Throttling:** Not in scope for MVP but could be implemented at a reverse proxy layer in the future if abuse becomes a concern.

* **Error Handling & Information Disclosure:**

  * As outlined in the "Error Handling Strategy," error messages returned to MCP clients (via MCP error objects) or logged to the console must not leak sensitive internal information such as stack traces, internal file paths, or raw database errors (from Fabric, if they were to occur and be relayed). Generic error messages with correlation IDs (for server-side log lookup) are preferred for client-facing errors when the detail is sensitive.

* **Logging:**

  * Ensure that logs, especially at `DEBUG` level, do not inadvertently include sensitive data from requests or responses. API keys are explicitly forbidden from being logged.
