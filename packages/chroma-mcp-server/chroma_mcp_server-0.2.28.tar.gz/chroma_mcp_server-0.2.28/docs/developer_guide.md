# Chroma MCP Server * Developer Guide

This guide provides instructions for developers working on the `chroma-mcp-server` codebase, including setup, testing, building, and releasing.

**Note on Ongoing Development:** This project is actively implementing the features outlined in the `docs/refactoring/local_rag_pipeline_plan_v4.md` roadmap, particularly focusing on the foundational Phase 1 capabilities (automated indexing, chat logging, working memory). Contributions towards the later phases (automated training, deployment) are welcome, but please coordinate with the project maintainers.

## Development Environment Setup

This project uses [Hatch](https://hatch.pypa.io/) for development and package management.

1. **Prerequisites:**
    * Python 3.10 or higher
    * Git
    * `curl` and `jq` (required by the `release.sh` script, will be deprecated in v0.3.0)
    * Hatch (Install globally if you don't have it: `pip install hatch`)

2. **Clone the Repository:**

    ```bash
    git clone https://github.com/djm81/chroma_mcp_server.git # Or your fork
    cd chroma_mcp_server
    ```

3. **Activate Hatch Environment:** Run the Hatch shell directly:

    ```bash
    hatch shell
    ```

    This command creates (if needed) and activates a virtual environment managed by Hatch, installing all necessary development dependencies listed in `pyproject.toml`.

4. **Configure Local MCP Servers (Optional, for Cursor):**
    If you intend to test integration with Cursor locally:
    * Copy the example configuration: `cp .cursor/mcp.example.json .cursor/mcp.json`
    * Edit `.cursor/mcp.json` and adjust environment variables as needed, especially:
        * `CHROMA_DATA_DIR`: Set a path for persistent storage.
        * `CHROMA_LOG_DIR`: Set a path for log files.
        * `LOG_LEVEL`: Adjust logging verbosity (e.g., `DEBUG`, `INFO`).
        * `CHROMA_EMBEDDING_FUNCTION`: Ensure consistency if set.
    * The `.cursor/mcp.json` file allows defining multiple server configurations. By convention, this project often includes:
        * `"chroma"`: Runs the version of `chroma-mcp-server` last installed locally via `uvx` (typically the production version installed by `release.sh`).
        * `"chroma_test"`: Configured to automatically fetch and run the *latest* version available on **TestPyPI**. This is useful for testing release candidates or development versions before a full production release.

    Here's an example snippet for the `chroma_test` configuration:

    ```json
    {
      "mcpServers": {
        "chroma_test": {
          "command": "uvx",
          "args": [
            "--refresh", // Ensures latest is checked
            "--default-index", "https://test.pypi.org/simple/", // Prioritize TestPyPI
            "--index", "https://pypi.org/simple/", // Fallback to PyPI
            "--index-strategy", "unsafe-best-match", // Strategy for finding packages
            "chroma-mcp-server@latest",
            "--client-type=ephemeral",
            "--embedding-function=default" // Example: Choose your embedding function
          ],
          "env": {
            "CHROMA_CLIENT_TYPE": "persistent",
            "CHROMA_DATA_DIR": "/path/to/your/test_data", // Use a separate test data dir
            "CHROMA_LOG_DIR": "/path/to/your/test_logs", // Use separate test logs
            "LOG_LEVEL": "DEBUG",
            "MCP_LOG_LEVEL": "DEBUG",
            "CHROMA_EMBEDDING_FUNCTION": "default" // Ensure consistency if set
          }
        },
        // ... other server definitions like "chroma"
      }
    }
    ```

    Remember to replace the placeholder paths for `CHROMA_DATA_DIR` and `CHROMA_LOG_DIR`.

## Development Scripts Overview

**DEPRECATION NOTICE:** The scripts in the `scripts/` directory are deprecated and will be removed in version 0.3.0. Please use the devtools commands installed with the Python package via Hatch:

* `hatch shell`: Activates the Hatch environment (replaces `develop.sh`).
* `hatch run test-mcp`: Runs tests with coverage and other options (replaces `test.sh`).
* `hatch run build-mcp`: Cleans the build directory and builds the package wheel (replaces `build.sh`).
* `hatch run publish-mcp`: Publishes the package to PyPI or TestPyPI (replaces `publish.sh`).
* `hatch run release-mcp`: Automates the full release process (replaces `release.sh`).

**Legacy scripts (deprecated):**

* `./scripts/test.sh`
* `./scripts/build.sh`
* `./scripts/publish.sh`
* `./scripts/test_uvx_install.sh`
* `./scripts/release.sh`

## Common Development Workflow

1. **Activate Environment:** Run `hatch shell`.
2. **Make Code Changes:** Edit the source code in the `src/` directory.
3. **Rebuild & Reinstall (Crucial!):** After making changes, especially to the server logic, CLI commands, or dependencies, you *must* rebuild and reinstall the package within the Hatch environment for the changes to take effect when using `hatch run` commands or potentially the development server script. Use:

    ```bash
    # Replace <version> with the actual version built
    hatch build && hatch run pip uninstall chroma-mcp-server -y && hatch run pip install 'dist/chroma_mcp_server-<version>-py3-none-any.whl[full,dev]'
    ```

4. **Run Tests:** Execute `./scripts/test.sh` to run the test suite. Add `--coverage` for a coverage report or `--clean` to force a rebuild of the test environment.

    ```bash
    # Using the script (recommended for matrix testing & coverage)
    ./scripts/test.sh # Runs test matrix

    # Or using hatch directly for the default environment
    hatch run test
    ```

5. **Build (Optional):** Run `./scripts/build.sh` to create a package wheel locally.
6. **Test Local Install (Optional):** Run `./scripts/test_uvx_install.sh` to verify the locally built wheel installs correctly via `uv pip install`.

## Running the Server Locally

There are several ways to run the server locally, depending on your goal (development, testing, or standard usage).

### Development Mode (Using Hatch)

While developing, the recommended way to run the server is using the provided wrapper script, which ensures it runs within the correct Hatch environment:

```bash
# Ensure you are in the project root directory
./scripts/run_chroma_mcp_server_dev.sh [OPTIONS]

# Example using ephemeral (in-memory) storage:
./scripts/run_chroma_mcp_server_dev.sh --client-type ephemeral

# Example using persistent (disk) storage:
./scripts/run_chroma_mcp_server_dev.sh --client-type persistent --data-dir ./dev_data --log-dir ./dev_logs

# Example connecting to an external ChromaDB instance running on localhost:8000:
# (Ensure the external ChromaDB server is already running!)
./scripts/run_chroma_mcp_server_dev.sh --client-type http --host localhost --port 8000

# Example connecting to ChromaDB Cloud:
# (Ensure required CHROMA_TENANT, CHROMA_DATABASE, CHROMA_API_KEY are set in .env)
./scripts/run_chroma_mcp_server_dev.sh --client-type cloud
```

This script internally uses `hatch run chroma-mcp-server-dev [OPTIONS]`. See the script content for details.

#### Logging in Stdio Mode

When the server runs in stdio mode (the default for MCP integrations like Cursor), all Python logging is now redirected to a dedicated log file instead of stderr/stdout to prevent contamination of the JSON communication stream. These logs are stored in the `CHROMA_LOG_DIR` directory (default: `./logs/`) with timestamp-based filenames:

```bash
logs/chroma_mcp_stdio_<timestamp>.log
```

This ensures clean JSON communication between the MCP client and server. The log level for stdio mode can be controlled with the `MCP_SERVER_LOG_LEVEL` environment variable.

#### Log Retention

To prevent log files from consuming excessive disk space, the server automatically cleans up log files older than the specified retention period. This cleanup happens during server startup. The retention period can be configured with the `LOG_RETENTION_DAYS` environment variable, which defaults to 7 days:

```bash
# Example setting in .env to keep logs for 14 days
LOG_RETENTION_DAYS=14
```

Alternatively, you can manually run the server directly within the activated Hatch environment:

```bash
# Ensure the Hatch environment is active (./scripts/develop.sh or hatch shell)
# Run the server using python -m
python -m chroma_mcp.cli [OPTIONS]

# Example with persistent storage:
python -m chroma_mcp.cli --client-type persistent --data-dir ./dev_data --log-dir ./dev_logs

# Example connecting to an external HTTP server:
python -m chroma_mcp.cli --client-type http --host localhost --port 8000
```

**Important:** When using `--client-type http` or `--client-type cloud`, the MCP server acts *only as a client*. You must have a separate ChromaDB server instance (e.g., running in Docker or via Chroma Cloud) accessible at the specified address or configured via cloud credentials.
The `ephemeral` and `persistent` modes manage a local ChromaDB instance directly.

**Automatic Collection Creation:** Upon startup, the server automatically checks for and creates essential ChromaDB collections (e.g., `codebase_v1`, `chat_history_v1`, `derived_learnings_v1`, `thinking_sessions_v1`, `validation_evidence_v1`, `test_results_v1`) if they are not already present. This ensures that the server is ready for use without requiring manual setup of these core collections.

For testing integration with tools like Cursor that use `uvx`, you might use the `release.sh` script to build, publish (e.g., to TestPyPI), and install that specific version for the `uvx chroma-mcp-server` command (see Releasing below).

### Standard Mode (Using Installed Package)

If you have installed the package via `pip` or `uvx` (e.g., `pip install chroma-mcp-server`), you can run it directly using the `chroma-mcp-server` command. Ensure any required environment variables (like `CHROMA_DATA_DIR` for persistent mode, or API keys for specific embedding functions) are set in your shell or via a `.env` file.

```bash
# Example using ephemeral mode
chroma-mcp-server --client-type ephemeral --embedding-function default

# Example using persistent mode (assuming CHROMA_DATA_DIR is set)
export CHROMA_DATA_DIR=/path/to/your/data
chroma-mcp-server --client-type persistent
```

### Via Smithery (for Local Execution)

[Smithery](https://smithery.ai/) acts as a registry and local launcher for MCP servers. AI clients like Claude Desktop can use Smithery to find, install, and run your server locally.

**Prerequisites:**

* Node.js and `npx` installed.
* The `chroma-mcp-server` package must be published to PyPI and registered with Smithery (see `docs/refactoring/hatch_smithery_integration.md`).

**Installation:**

Users (or clients) can install the server via the Smithery CLI. This typically uses `pip` under the hood to install the package from PyPI into a managed environment.

```bash
npx -y @smithery/cli install chroma-mcp-server
```

**Running:**

Clients launch the server using the `run` command, optionally providing configuration:

```bash
# Run with default configuration (defined in smithery.yaml)
npx -y @smithery/cli run chroma-mcp-server

# Run with custom configuration (persistent mode)
npx -y @smithery/cli run chroma-mcp-server --config '{ "clientType": "persistent", "dataDir": "./my_chroma_data" }'
```

The Smithery CLI reads the `smithery.yaml` file within the installed package, executes the `commandFunction` (which sets environment variables and calls `chroma-mcp-server`), and manages the `stdio` communication with the client.

**Note:** As detailed in the [Smithery Integration Guide](docs/refactoring/hatch_smithery_integration.md), this server only supports local execution via Smithery. Online hosting (Smithery Deployments) is **not** supported due to potential interaction with local sensitive data.

## Automated Chat Logging

This project includes capabilities for automatically logging summaries of AI chat interactions to ChromaDB, facilitated by IDE rules (e.g., `.cursor/rules/auto_log_chat.mdc`).

There are two main ways to log chat interactions:

1. **Automatic Logging via IDE Rules**: Using the `auto_log_chat` rule in Cursor or other supported IDEs, which instructs the AI to automatically log each interaction. See the [Automated Chat History Logging Guide](docs/integration/automated_chat_logging.md) for setup details.

2. **Manual Logging via CLI**: Using the `chroma-mcp-client log-chat` command to manually log chat interactions with rich context:

```bash
# Basic usage
chroma-mcp-client log-chat --prompt-summary "User question" --response-summary "AI response"

# Full usage with detailed context
chroma-mcp-client log-chat \
  --prompt-summary "User question" \
  --response-summary "AI response" \
  --raw-prompt "Full text of the question" \
  --raw-response "Full text of the response" \
  --tool-usage-file tools.json \
  --file-changes-file changes.json \
  --involved-entities "file.js,function_name" \
  --modification-type "feature" \
  --confidence-score 0.85
```

See the [CLI Reference](scripts/chroma-mcp-client.md#log-chat) for full details of command options.

## Working Memory and Thinking Tools

## Developer Workflow: Implicit Learning & Manual Promotion

This workflow describes how developers can analyze their chat history to identify valuable insights and manually promote them into the `derived_learnings_v1` collection for reuse by the RAG system.

### Overview

The process involves two main CLI commands:

1. `chroma-mcp-client analyze-chat-history`: This command scans the `chat_history_v1` collection for entries (typically those with status `captured`), attempts to correlate them with recent code changes in your Git repository, and updates their status to `analyzed`. It outputs a list of entries it successfully processed.
2. `chroma-mcp-client promote-learning`: After reviewing the output of the analysis, the developer uses this command to manually create a structured learning entry in the `derived_learnings_v1` collection. This command also updates the status of the source chat entry to `promoted_to_learning`.

### Step-by-Step Guide

1. **Run Analysis on Chat History:**

    Execute the `analyze-chat-history` command. You'll typically want to specify how many days back to look and the path to your repository.

    ```bash
    # Example: Analyze chats from the last 7 days in the current repo
    hatch run chroma-mcp-client analyze-chat-history --days-limit 7 --repo-path .

    # Example: Analyze chats from the last 30 days, specifying collection names
    hatch run chroma-mcp-client analyze-chat-history --days-limit 30 --collection-name chat_history_v1 --chat-collection-name chat_history_v1 --repo-path /path/to/your/project
    ```

    Key options:
    * `--days-limit INT`: How many days back to fetch entries for analysis.
    * `--repo-path TEXT`: Path to the root of the Git repository for code correlation.
    * `--collection-name TEXT`: The chat history collection to analyze (default: `chat_history_v1`).

    The command will output a list of chat entry IDs and their summaries that were updated to `analyzed` status.

2. **Identify Learnings for Promotion:**

    Review the output from the `analyze-chat-history` command. Look for chat interactions that represent a useful pattern, solution, or piece of knowledge worth capturing formally.

3. **Gather Information for `promote-learning`:**

    Once you've identified a chat entry to promote (e.g., ID `chat_entry_xyz`), gather the following details:

    * `--source-chat-id TEXT`: The ID of the chat entry from `chat_history_v1` (e.g., `chat_entry_xyz`). This is optional but highly recommended for traceability.
    * `--description TEXT`: **(Required)** A concise, human-readable description of the learning or insight. This becomes the main document content in `derived_learnings_v1`.
    * `--pattern TEXT`: **(Required)** A more generalized statement of the pattern or rule derived from the specific interaction.
    * `--code-ref TEXT`: **(Required)** A reference to a relevant code snippet, typically a `chunk_id` from the `codebase_v1` collection. The `chunk_id` has the format `relative_file_path:commit_sha:chunk_index` (e.g., `src/module/file.py:abcdef1234567890abcdef1234567890abcdef12:0`).
    * `--tags TEXT`: **(Required)** A comma-separated string of relevant keywords or tags (e.g., `python,api,refactoring,typer`).
    * `--confidence FLOAT`: **(Required)** A float between 0.0 and 1.0 indicating your confidence in this learning.
    * `--collection-name TEXT`: The target collection for the new learning (default: `derived_learnings_v1`).
    * `--chat-collection-name TEXT`: The source chat history collection (default: `chat_history_v1`), used if `source-chat-id` is provided to update its status.

4. **Execute Promotion:**

    Use the `promote-learning` command with the gathered information. You can use the wrapper script directly or the hatch alias (`promote-learn`).

    ```bash
    # Example promotion using the hatch alias
    hatch run promote-learn \
        --source-chat-id "chat_entry_xyz" \
        --description "When implementing a FastAPI endpoint that requires background tasks, use BackgroundTasks to ensure the response is sent quickly while tasks run separately." \
        --pattern "FastAPI endpoints needing deferred work should use BackgroundTasks for non-blocking operations." \
        --code-ref "src/my_app/api/endpoints.py:commitsha123abc:3" \
        --tags "fastapi,backgroundtasks,python,api-design" \
        --confidence 0.95
    ```

    The command will output the ID of the newly created learning in `derived_learnings_v1` and confirm the status update of the source chat entry.

5. **Verification (Optional):**

    You can verify the promotion using `chroma-mcp-client query` or MCP tools:

    * Query `derived_learnings_v1` for the new learning ID to inspect its content.
    * Query `chat_history_v1` for the `source-chat-id` to confirm its status is `promoted_to_learning` and that it has a `promoted_learning_id` metadata field pointing to the new learning.

This workflow enables a systematic way to build up a high-quality `derived_learnings_v1` collection from practical development interactions.

## Testing

Tests are located in the `tests/` directory and use `pytest`. Run tests using the script:

```bash
# Run all tests across the Python matrix (defined in pyproject.toml)
# Using the script (recommended for matrix testing & coverage)
# This uses hatch run test:run internally for matrix.
./scripts/test.sh # Runs test matrix

# Or run tests only for the default environment using Hatch
hatch run test

# If you want to see more verbose output, use the -v flag:
./scripts/test.sh -v

# Run tests across the matrix and generate coverage reports.
# This runs tests first, then combines data, then generates:
# 1. Terminal report (with missing lines)
# 2. XML report (coverage.xml for Codecov)
./scripts/test.sh --coverage 
# or shorthand:
./scripts/test.sh -c

# Run tests across the matrix and generate an HTML coverage report.
# This runs tests first, then combines data, then generates the report
# in the coverage_html/ directory (as configured in pyproject.toml).
./scripts/test.sh --html

# Force environment rebuild before testing (useful if dependencies change)
./scripts/test.sh --clean

# Run tests for specific files or directories
./scripts/test.sh tests/tools/test_auto_log_chat_bridge.py
./scripts/test.sh tests/chroma_mcp_client/

# Run tests on a specific Python version only
./scripts/test.sh --python 3.10  # or --py 3.10
./scripts/test.sh --py 3.11 tests/tools/  # Run tools tests on Python 3.11 only

# Run tests with automated test workflow capture
# This automatically tracks test failures and transitions to success
./scripts/test.sh --auto-capture-workflow
./scripts/test.sh -c -v --auto-capture-workflow  # With coverage and verbose output
```

Note that coverage reports (`terminal`, `XML`, `HTML`) are generated *after* all tests across all configured Python versions have completed.

```bash
# Run specific tests within the Hatch environment
hatch run test:run tests/tools/test_collection_tools.py::TestCollectionTools::test_create_collection_success
```

### Automated Test Workflow

The automated test-driven learning workflow captures test failures, monitors for fixes, and creates validation evidence when tests transition from failing to passing:

```bash
# Set up the test workflow (creates Git hooks)
chroma-mcp-client setup-test-workflow

# This creates/modifies:
# - pre-push hook: Runs tests with --auto-capture-workflow
# - post-commit hook: Checks for test transitions after code changes
# Note: The setup preserves existing post-commit hook content such as codebase indexing

# Run tests with automatic workflow capture
./scripts/test.sh -c -v --auto-capture-workflow

# Manually check for test transitions
chroma-mcp-client check-test-transitions

# Check and auto-promote valid transitions
chroma-mcp-client check-test-transitions --auto-promote
```

For full details, see the [Automated Test Workflow Guide](usage/automated_test_workflow.md).

## Building the Package

Use the provided script or Hatch directly:

```bash
# Using the script (cleans first)
./scripts/build.sh

# Or manually with Hatch
hatch build
```

This will generate the distributable files (wheel and sdist) in the `dist/` directory.

## Publishing to PyPI/TestPyPI

The `publish.sh` script handles publishing the built package (`dist/` directory) to PyPI or TestPyPI. It requires the target (`-t` for TestPyPI, `-p` for PyPI) and the version (`-v`). Credentials can be supplied via environment variables (`PYPI_USERNAME`, `PYPI_PASSWORD`) or interactively.

```bash
# Publish version 0.2.0 to TestPyPI
./scripts/publish.sh -t -v 0.2.0

# Publish version 0.2.0 to Production PyPI
./scripts/publish.sh -p -v 0.2.0
```

**Note:** Publishing to PyPI is usually handled automatically as part of the `release.sh` script.

## Registering with Smithery

After successfully publishing a version to PyPI, you need to make it discoverable by clients using the Smithery ecosystem. This is done via the Smithery website, **not** the `@smithery/cli` tool (which is primarily for installing/running servers).

**Steps:**

1. **Publish to PyPI:** Ensure the desired package version is available on PyPI.
2. **Go to Smithery Website:** Visit [https://smithery.ai/](https://smithery.ai/).
3. **Login/Sign Up:** Authenticate with your account (likely linked to GitHub).
4. **Add/Claim Server:** Find the option to add a new server or claim an existing one if it was automatically discovered.
5. **Configure Repository:** Link the Smithery entry to your GitHub repository (`djm81/chroma_mcp_server`).
6. **Configure Settings:** Within the server settings on the Smithery website:
    * Ensure the `smithery.yaml` file in your repository is detected.
    * **Crucially, configure the server for local execution.** Look for settings related to deployment or execution type and ensure it's set to only allow local runs initiated by the client via `npx @smithery/cli run ...`, rather than enabling online hosting (Smithery Deployments).

Once configured on the website, clients should be able to find `chroma-mcp-server` and use `npx @smithery/cli install/run` as described in the "Via Smithery (for Local Execution)" section under "Running the Server Locally".

## Releasing a New Version

The `release.sh` script provides a streamlined process for releasing a new version:

0. **Before Release Preparation:**
   * Update `CHANGELOG.md` with a new section documenting all notable changes in this version
   * Ensure the version number is updated in `pyproject.toml`
   * Verify all tests are passing with adequate coverage

1. Prompts for the version number (if not provided via `--version`).
2. Builds the package wheel.
3. Uploads to TestPyPI first (unless `--prod-only` is specified).
4. Uploads to Production PyPI (unless `--test-only` is specified).
5. Installs the newly released version (from PyPI or TestPyPI based on `--update-target`) locally for use with the standard `uvx chroma-mcp-server` command.

```bash
# Run interactively, prompted for version and options
./scripts/release.sh

# Release version 0.2.0 non-interactively, update local uvx from Prod PyPI
./scripts/release.sh --version 0.2.0 -y --update-target prod

# Run only TestPyPI steps for version 0.2.1
./scripts/release.sh --version 0.2.1 --test-only
```

For all options:

```bash
./scripts/release.sh --help
```

## Dependencies

* **Core:** `python-dotenv`, `pydantic`, `fastapi`, `uvicorn`, `chromadb`, `fastmcp`, `numpy`, `onnxruntime`.
* **Optional (`[full]`):** `sentence-transformers`, `httpx`.
* **Development (`dev`):** `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `pytest-xdist`, `black`, `isort`, `mypy`, `pylint`, `types-PyYAML`.

See `pyproject.toml` for specific version constraints.

## Troubleshooting

* **UVX Cache Issues:** If `uvx` seems stuck on an old version after a release or install, try refreshing its cache: `uvx --refresh chroma-mcp-server --version`
* **Dependency Conflicts:** Ensure your Hatch environment is clean (`hatch env remove default && hatch env create`) or run tests with `./scripts/test.sh --clean`.
* **Release Script Errors:** Ensure `curl` and `jq` are installed. Check PyPI/TestPyPI credentials if publishing fails.
* **Embedding Function Mismatch Errors:** If you change the embedding function (via `.env` or `--embedding-function` argument) for a project with existing ChromaDB collections, subsequent operations (like queries or using the analysis client) might fail with an `Embedding function name mismatch` error. This means the embedding function your client is *currently* configured to use doesn't match the function name stored in the collection's metadata. To fix this, use the `chroma-mcp-client update-collection-ef` command to update the collection's metadata to match your current client setting. See the [chroma-mcp-client documentation](scripts/chroma-mcp-client.md#update-collection-ef) for usage.

## CLI Arguments

These arguments apply when running the server directly (e.g., `chroma-mcp-server` or `python -m chroma_mcp.cli`).

* `--mode [stdio|http]`: Server communication mode. Default: `http`.
* `--client-type [ephemeral|persistent|http|cloud]`: ChromaDB backend connection type. Default: `ephemeral`.
* `--data-dir PATH`: Path for persistent data storage (used with `--client-type persistent`).
* `--log-dir PATH`: Directory for log files.
* `--host TEXT`: Host address for `--client-type http`.
* `--port INTEGER`: Port number for `--client-type http`.
* `--ssl / --no-ssl`: Use SSL for `--client-type http`. Default: `--no-ssl`.
* `--tenant TEXT`: Tenant ID for `--client-type cloud`.
* `--database TEXT`: Database name for `--client-type cloud`.
* `--api-key TEXT`: API key for `--client-type cloud`.
* `--cpu-execution-provider [auto|true|false]`: Configures ONNX execution provider usage (for `default`/`fast` embedding functions). Default: `auto`.
* `--embedding-function TEXT`: Specifies the embedding function to use. Choices include `default`, `fast`, `accurate`, `openai`, `cohere`, `huggingface`, `voyageai`, `google`, `bedrock`, `ollama`. Default: `default`.
* `--version`: Show version and exit.
* `-h`, `--help`: Show help message and exit.

Environment variables often override these defaults. See the `.env.template` file for corresponding variable names.

Key environment variables (set in `.env`):

* `CHROMA_CLIENT_TYPE`: `persistent`, `http`, `cloud`, etc.
* `CHROMA_DATA_DIR`: Path for persistent data.
* `LOG_LEVEL`: Sets the default logging level for server components and the client CLI (if not overridden by the client's `-v`/`--verbose` flags).
* `MCP_LOG_LEVEL`: Sets the logging level specifically for MCP framework components.
* `MCP_SERVER_LOG_LEVEL`: Controls logging level for stdio mode, which uses per-execution log files.
* `CHROMA_EMBEDDING_FUNCTION`: `default`, `accurate`, `openai`, etc.
* API keys (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.) as needed for embedding functions.

### Timestamp Enforcement

The server automatically enforces the use of system-generated timestamps for all documents stored in ChromaDB collections. This prevents inconsistencies that can occur when AI models use their training cutoff dates instead of the current system time when generating timestamps. This feature is particularly important for:

* `chat_history_v1` - Chat logs stored with accurate timestamps rather than model perception date
* `thinking_sessions_v1` - Sequential thinking records with accurate timestamps
* Other collections with timestamp metadata

No configuration is needed for this feature as it's implemented at the server level in the document and collection tools.

### Promoting Learnings (Manual Workflow)

While the goal is often automated analysis, manual curation is crucial for high-quality derived learnings.

1. **Analyze:** Run `analyze-chat-history` to correlate recent chats with code changes and mark potentially valuable entries as `analyzed`:

    ```bash
    hatch run chroma-mcp-client analyze-chat-history --days-limit 3
    ```

2. **Review (Outside Script):** Examine the output of `analyze-chat-history` or query the `chat_history_v1` collection directly (e.g., using MCP tools) to find entries marked `analyzed` that represent useful insights.
3. **Promote:** Use the `promote-learning` command to create a structured entry in `derived_learnings_v1`. You'll need the source chat entry ID and details like the core pattern, tags, confidence, and a relevant code reference (chunk ID).

    ```bash
    # Example promoting chat entry 'abc-123'
    hatch run chroma-mcp-client promote-learning \
        --source-chat-id "abc-123" \
        --description "Refactored logging setup for better context." \
        --pattern "logging.basicConfig(...) replaced with custom setup" \
        --code-ref "src/utils/logging.py:sha456:0-15" \
        --tags "python,logging,refactor" \
        --confidence 0.9
    ```

### Promoting Learnings (Interactive Workflow - Recommended)

To streamline the review and promotion process, use the `review-and-promote` command. This provides a more user-friendly, guided experience:

1. **Analyze:** Run `analyze-chat-history` as described above.
2. **Review and Promote Interactively:** Start the interactive workflow:

    ```bash
    hatch run review-and-promote --days-limit 3 
    # Or alias: hatch run review-promote --days-limit 3
    ```

    The script will:
    * Fetch chat entries marked as 'analyzed' within the specified time frame.
    * Display each entry's summary.
    * Query the `codebase_v1` collection for relevant code snippets based on the chat summary and display potential `code_ref` candidates.
    * Prompt you to **Promote (p)**, **Ignore (i)**, **Skip (s)**, or **Quit (q)**.
    * If promoting, guide you through entering the pattern, tags, confidence, and selecting/entering the `code_ref`.
    * Automatically update the source chat entry status to `promoted_to_learning` or `ignored`.

3. **Enhanced Features (New):**
    * **Auto-Promote:** Enable automatic promotion of high-confidence entries:

      ```bash
      hatch run review-promote --auto-promote --auto-promote-threshold 0.75
      ```

    * **Smart Defaults:** All fields now have intelligent defaults based on context, allowing you to just press Enter in most cases.
    * **Low Confidence Warnings:** Visual warnings help identify entries that may need more careful review.
    * **Enhanced Code Selection:** Better bidirectional linking makes code reference selection more accurate.

This interactive command significantly simplifies the process of curating the `derived_learnings_v1` collection.

## Querying for RAG

## Codebase Indexing

The system includes several tools for indexing code content from your codebase into ChromaDB for future retrieval:

### Semantic Chunking

Codebase indexing now uses semantic chunking by default, which preserves logical code structures like functions and classes when creating chunks. This improves retrieval quality by ensuring that queries return complete logical units rather than arbitrary fragments of code.

Key benefits include:

* Better context preservation for function definitions, classes, and methods
* Improved bi-directional linking between chat discussions and code changes
* More effective RAG with chunks that follow logical boundaries

For details on how semantic chunking works, see the [Semantic Chunking documentation](usage/semantic_chunking.md).

### Using the Index Command

The primary tool is the `chroma-mcp-client index` command, which has several usage patterns:

```bash
# Index all git-tracked files in the repository
chroma-mcp-client index --all

# Index specific files
chroma-mcp-client index path/to/file1.py path/to/file2.js

# Index specific files with a non-default collection
chroma-mcp-client index path/to/file1.py path/to/file2.js --collection-name my_custom_collection
```

The indexer scans files, splits them into semantic chunks, calculates embeddings, and stores them in ChromaDB for later retrieval. All this happens on the server side using the configured embedding function.

### Git Integration

The Chroma MCP Server includes tools for integrating with Git to enable automatic indexing of code changes. This ensures that your codebase index always reflects the latest state of your project.

#### Setup Git Hooks for Automatic Indexing

You can set up Git hooks to automatically index changed files whenever you make a commit:

```bash
# Using the CLI tool to set up Git hooks
chroma-mcp-client setup-git-hooks
```

This command creates a `post-commit` hook in your `.git/hooks/` directory that automatically detects and indexes files that were changed in each commit.

#### Automatic Test Workflow Integration

The Git integration also supports the automated test-driven learning workflow:

```bash
# Set up both indexing and test workflow hooks
chroma-mcp-client setup-test-workflow
```

This creates both `pre-push` and `post-commit` hooks that handle test execution, failure/success tracking, and automatic correlation with code changes.

#### How Automatic Indexing Works

The Git hook integration:

1. Runs automatically after every successful `git commit`
2. Uses `git diff-tree` to find files added or modified in the commit
3. Passes only the changed files to the indexer, making it efficient
4. Uses semantic chunking to preserve logical code structures
5. Stores the indexed content in the configured ChromaDB collection

#### Manual Indexing

You can also manually trigger indexing of your entire codebase:

```bash
# Index all git-tracked files
chroma-mcp-client index --all

# Or index specific files
chroma-mcp-client index path/to/file1.py path/to/file2.js
```

For more details on the Git hook implementation and customization options, see the [Git Hooks documentation](automation/git_hooks.md).
