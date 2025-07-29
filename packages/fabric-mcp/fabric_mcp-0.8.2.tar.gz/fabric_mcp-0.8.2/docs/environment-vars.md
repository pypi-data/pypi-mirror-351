# Environment Variables Documentation

This document details the environment variables used to configure the Fabric MCP Server.

* **`FABRIC_BASE_URL`**
  * **Description:** The base URL of the running Fabric REST API server (`fabric --serve`).
  * **Default:** `http://127.0.0.1:8080`
  * **Required:** No (uses default if not set).
  * **Component Using It:** Fabric API Client (`api_client.py`).

* **`FABRIC_API_KEY`**
  * **Description:** The API key required to authenticate with the Fabric REST API server, if the Fabric instance is configured to require one.
  * **Default:** None (Authentication is not attempted by `fabric-mcp` if this variable is not set).
  * **Required:** No (depends on Fabric server configuration).
  * **Component Using It:** Fabric API Client (`api_client.py`).
  * **Security Note:** This is a sensitive value. It should be handled securely and not exposed in logs or version control.

* **`FABRIC_MCP_LOG_LEVEL`**
  * **Description:** Sets the logging verbosity for the Fabric MCP Server itself.
  * **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (case-insensitive).
  * **Default:** `INFO`
  * **Required:** No (uses default if not set).
  * **Component Using It:** CLI Handler (`cli.py`) and Logging setup.

These variables are typically loaded by the "Configuration Component" described in the main Architecture Document.
