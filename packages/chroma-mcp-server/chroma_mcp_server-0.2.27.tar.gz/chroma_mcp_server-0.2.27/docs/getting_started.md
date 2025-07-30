# Getting Started with Chroma MCP Server

This guide will help you set up and start using the Chroma MCP Server.

**Note on Ongoing Development:** The Chroma MCP Server is actively being developed to implement the full vision outlined in the `docs/refactoring/local_rag_pipeline_plan_v4.md` roadmap, which includes advanced features like automated learning pipelines (Phases 2 and 3). While the core setup and foundational features (like automated indexing via Git hooks and automated chat logging via IDE rules - Phase 1) are functional, some of the more sophisticated capabilities described in related documents are still under active development.

## Prerequisites

- Python 3.10 or higher
- Pip package manager
- Git (optional, for development)

## Installation

Choose your preferred installation method:

### Option 1: Simple Installation (pip/uvx)

The base `chroma-mcp-server` package provides core functionality. You can enhance it by installing optional dependencies for specific features.

**Base Installation:**

```bash
# Install the base package from PyPI using pip
pip install chroma-mcp-server

# Or using uv
uv pip install chroma-mcp-server
```

**Optional Features (Extras):**

The server offers several "extras" to install sets of optional dependencies:

- `[aimodels]`: Installs support for a wide range of embedding models from providers like OpenAI, Google, Cohere, HuggingFace, VoyageAI, AWS Bedrock, and Ollama. This is recommended if you plan to use embedding functions beyond the default CPU-based ones.
- `[server]`: Includes `httpx`, which might be needed if the server itself needs to make outbound HTTP requests (e.g., for webhooks or fetching external resources).
- `[client]`: Includes `GitPython`, useful for more robust Git interactions if you are using client-side scripts that analyze or index Git repositories.

You can install one or more extras:

```bash
# Install with AI model support
pip install "chroma-mcp-server[aimodels]"
uv pip install "chroma-mcp-server[aimodels]"

# Install with AI model and server HTTP client support
pip install "chroma-mcp-server[aimodels,server]"
uv pip install "chroma-mcp-server[aimodels,server]"
```

**Full Installation (Recommended for most users wanting all features):**

To install the server with all common optional features (including all AI models, server utilities, and client utilities), you can use a combined set of extras.
A convenience `[full]` extra is defined in `pyproject.toml` to include `aimodels`, `server`, and `client`:

```bash
# For full functionality including all optional embedding models and utilities
pip install "chroma-mcp-server[full]" 
# Or using uv
uv pip install "chroma-mcp-server[full]"
```

### Option 2: Via Smithery (for Local Execution)

[Smithery](https://smithery.ai/) provides a registry and CLI tool for managing MCP servers, often used by AI clients like Claude Desktop. This method still runs the server locally.

**Prerequisites:**

- Node.js and `npx` must be installed.
- The `chroma-mcp-server` package must be published on PyPI and registered on the Smithery website ([https://smithery.ai/](https://smithery.ai/)).

**Installation:**

```bash
# Install the package into a Smithery-managed environment
npx -y @smithery/cli install chroma-mcp-server

# If prompted or required by Smithery configuration, provide a key:
# npx -y @smithery/cli install chroma-mcp-server --key YOUR_API_KEY
```

### Option 3: Development Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/djm81/chroma_mcp_server.git # Use your repo URL
    cd chroma_mcp_server
    ```

2. **Install Hatch:** If you don't have it, install Hatch globally:

    ```bash
    pip install hatch
    ```

3. **Activate Environment:** Use the devtools command or `hatch shell`:

**DEPRECATION NOTICE:** `./scripts/develop.sh` is deprecated and will be removed in version 0.3.0.

```bash
# Recommended: Activate the Hatch development environment
hatch run develop-mcp

# Or directly with Hatch shell
hatch shell
```

This sets up the environment with all necessary development dependencies.

## Development Scripts

**DEPRECATION NOTICE:** The scripts in the `scripts/` directory are deprecated and will be removed in version 0.3.0. Please use the devtools commands installed via the Python package, e.g., via Hatch:

```bash
# Start development environment
hatch run develop-mcp  # replaces ./scripts/develop.sh

# Build the package
hatch run build-mcp  # replaces ./scripts/build.sh

# Run tests with coverage
hatch run test-mcp  # replaces ./scripts/test.sh

# Publish to PyPI/TestPyPI
hatch run publish-mcp [-t|-p] [-v VERSION]  # replaces ./scripts/publish.sh

# Test UVX installation from local wheel
./scripts/test_uvx_install.sh  # deprecated (no direct devtools replacement)

# Automate the full release process (includes installing Prod/Test version locally)
hatch run release-mcp [--update-target <prod|test>] <VERSION>  # replaces ./scripts/release.sh
```

## Configuration

Copy the example `.env.template` to `.env` and adjust values as needed:

```bash
cp .env.template .env
```

The server primarily uses environment variables for configuration. A `.env` file in the project root is loaded automatically. Key variables include:

- `CHROMA_CLIENT_TYPE`: Specifies how the MCP server connects to or manages ChromaDB. Available options:
  - `ephemeral` (Default): Runs an in-memory ChromaDB instance. Data is lost when the server stops. Good for quick tests or stateless operations.
  - `persistent`: Creates or uses a local, disk-based ChromaDB instance. Requires `CHROMA_DATA_DIR` to be set to a valid path. Data persists between server restarts.
  - `http`: Connects to an **external, already running** ChromaDB server via HTTP/HTTPS. Requires `CHROMA_HOST` and `CHROMA_PORT` (and optionally `CHROMA_SSL`, `CHROMA_HEADERS`) to be set. The MCP server acts only as a client.
  - `cloud`: Connects to a ChromaDB Cloud instance. Requires `CHROMA_TENANT`, `CHROMA_DATABASE`, and `CHROMA_API_KEY` to be set. The MCP server acts only as a client.
- `CHROMA_DATA_DIR`: Path for persistent storage (required and only used if `CHROMA_CLIENT_TYPE=persistent`).
- `CHROMA_LOG_DIR`: Path for log files (defaults to a temporary directory).
- `LOG_RETENTION_DAYS`: Number of days to keep log files before automatic cleanup during server startup (defaults to 7 days).
- `LOG_LEVEL`: Sets the default logging level for server components and the client CLI (if not overridden by `-v`/`--verbose`).
- `MCP_LOG_LEVEL`: Sets the logging level specifically for the MCP framework components (e.g., `INFO`, `DEBUG`).
- `MCP_SERVER_LOG_LEVEL`: Controls logging level specifically for the stdio server mode. In stdio mode, logs are redirected to timestamp-based log files (e.g., `logs/chroma_mcp_stdio_1747049137.log`) to prevent contamination of the JSON communication stream.
- `CHROMA_EMBEDDING_FUNCTION`: Specifies the embedding function to use (e.g., `default`, `accurate`, `openai`). See README or API reference for all options. Requires API keys for non-local models.
- API Keys: If using API-based embedding functions (like `openai`, `gemini`), ensure the relevant environment variables (e.g., `OPENAI_API_KEY`, `GOOGLE_API_KEY`) are set.
- Connection Details (`http`/`cloud` modes):
  - `CHROMA_HOST`, `CHROMA_PORT`, `CHROMA_SSL`: Required for `http` mode.
  - `CHROMA_HEADERS`: Optional HTTP headers (JSON string) for `http` mode.
  - `CHROMA_TENANT`, `CHROMA_DATABASE`, `CHROMA_API_KEY`: Required for `cloud` mode.

**Automatic Collection Creation:**
Upon startup, the Chroma MCP Server automatically checks for and creates essential ChromaDB collections (e.g., `codebase_v1`, `chat_history_v1`, `derived_learnings_v1`, `thinking_sessions_v1`, `validation_evidence_v1`, `test_results_v1`) if they are not already present. This ensures that the server is ready for use without requiring manual setup of these core collections. This behavior simplifies initial setup, especially when using persistent storage for the first time.

**Note on Embedding Function Consistency for Collections:**
If you modify the `CHROMA_EMBEDDING_FUNCTION` environment variable (or the corresponding `--embedding-function` CLI argument for server startup) after collections like `codebase_v1` have already been created, you may encounter `Embedding function name mismatch` errors when client tools (e.g., `review-and-promote`, MCP server queries) try to access them. This happens because these tools often expect collections to use a specific embedding model (e.g., 'accurate' for `codebase_v1`).

To resolve this:

- For `codebase_v1`: The recommended approach is often to delete the existing collection and re-index your codebase using `hatch run index-codebase` (or `chroma-mcp-client index --all`). This ensures it's created with the 'accurate' model, which is the default for indexing and querying.
- For other collections, or if re-indexing `codebase_v1` is not feasible: You can use the `chroma-mcp-client update-collection-ef --collection <n> --ef <new_ef_name>` command to update the collection's metadata to reflect the new embedding function name. Be cautious with this, as it only changes the metadata pointer; the actual embeddings are not recomputed. This is usually suitable if the actual embedding *model* hasn't changed, only its registered name or how the client refers to it.
- Alternatively, use `chroma-mcp-client setup-collections` to recreate all required collections with the current embedding function configuration.

See the [chroma-mcp-client script documentation](scripts/chroma-mcp-client.md) for details on `update-collection-ef` and `setup-collections`.

**Note on Timestamp Consistency:**
The server enforces consistent timestamp handling by automatically overriding any AI-provided timestamps with server-generated values. This ensures that all documents stored in ChromaDB collections have accurate system timestamps, addressing potential issues where AI models might use their training cutoff dates instead of the actual system time.

**Automated Test Workflow Configuration:**
To set up the automated test-driven learning workflow, you can use the `setup-test-workflow` command from the CLI:

```bash
# Set up automated test workflow Git hooks and configuration
chroma-mcp-client setup-test-workflow --workspace-dir /path/to/workspace

# Run tests with automatic test failure/success tracking
./scripts/test.sh -c -v --auto-capture-workflow
```

This will create Git hooks that automatically track test executions and transitions from failure to success. For more details, see the [Automated Test Workflow Guide](usage/automated_test_workflow.md).

### Git Integration for Codebase Indexing

The Chroma MCP Server includes automated Git hooks for keeping your codebase index up to date. This ensures that your RAG system always has access to the latest code in your repository.

#### Setting Up Git Hooks for Automatic Indexing

You can use the `setup-git-hooks` command to automatically set up Git hooks:

```bash
# Set up Git hooks for automatic indexing
chroma-mcp-client setup-git-hooks
```

This creates a `post-commit` hook that automatically indexes any files changed in each commit.

#### Manual Setup

If you prefer to set up the hooks manually:

1. **Create a post-commit hook file:**

   ```bash
   # Navigate to your git hooks directory
   cd .git/hooks
   
   # Create the post-commit file
   touch post-commit
   chmod +x post-commit
   ```

2. **Add the following content to the post-commit file:**

   ```bash
   #!/bin/sh
   # .git/hooks/post-commit
   
   echo "Running post-commit hook: Indexing changed files..."
   
   # Ensure we are in the project root
   PROJECT_ROOT=$(git rev-parse --show-toplevel)
   cd "$PROJECT_ROOT" || exit 1
   
   # Get list of changed/added files in the last commit
   # Use --diff-filter=AM to only get Added or Modified files
   FILES=$(git diff-tree --no-commit-id --name-only -r HEAD --diff-filter=AM -- "*.py" "*.js" "*.ts" "*.md" "*.txt")
   
   if [ -z "$FILES" ]; then
     echo "No relevant files changed in this commit."
     exit 0
   fi
   
   echo "Files to index:"
   echo "$FILES"
   
   # Run the indexer
   FILES_ARGS=$(echo "$FILES" | tr '\n' ' ')
   
   # Run the client with appropriate verbosity
   chroma-mcp-client index $FILES_ARGS
   
   if [ $? -ne 0 ]; then
     echo "Error running chroma-mcp-client indexer!"
     exit 1
   fi
   
   echo "Post-commit indexing complete."
   exit 0
   ```

#### Initial Codebase Indexing

After setting up the hooks, you'll want to index your existing codebase:

```bash
# Index all tracked files in the repository
chroma-mcp-client index --all
```

This will scan your repository and index all relevant files into the `codebase_v1` collection.

For more details on automatic indexing, see the [Git Hooks documentation](automation/git_hooks.md).

Cursor uses `.cursor/mcp.json` to configure server launch commands:

```json
{
  "mcpServers": {
    "chroma": { // Runs the version last installed via uvx (typically Prod)
      "command": "uvx",
      "args": [
        "chroma-mcp-server",
        "--client-type=persistent",
        "--embedding-function=default" // Example: Choose your embedding function
      ],
      "env": {
        "CHROMA_DATA_DIR": "/path/to/data/dir", // Replace with your actual path
        "CHROMA_LOG_DIR": "./logs",
        "LOG_LEVEL": "INFO",
        "MCP_LOG_LEVEL": "INFO"
      }
    },
    "chroma_test": { // Runs the latest version from TestPyPI
      "command": "uvx",
      "args": [
        "--default-index", "https://test.pypi.org/simple/",
        "--index", "https://pypi.org/simple/",
        "--index-strategy", "unsafe-best-match",
        "chroma-mcp-server@latest"
      ],
      "env": { ... }
    }
  }
}
```

### Running Specific Versions

- The `chroma_test` entry automatically runs the latest from TestPyPI.
- The `chroma` entry runs the version last installed by `uvx`. The `release.sh` script handles installing the released version (from PyPI or TestPyPI via `--update-target`) for this entry.
- To manually run a specific version with the `chroma` entry, install it directly:

  ```bash
  # Install prod version 0.1.11
  uvx --default-index https://pypi.org/simple/ chroma-mcp-server@0.1.11
  
  # Install test version 0.1.11
  uvx --default-index https://test.pypi.org/simple/ --index https://pypi.org/simple/ --index-strategy unsafe-best-match chroma-mcp-server@0.1.11
  ```

After installing, restart the `chroma` server in Cursor.

### Automated Chat History Logging

Leveraging the MCP integration, the server supports automatically logging summaries of AI chat interactions into a dedicated ChromaDB collection. This provides a persistent record for analysis and context retrieval.

See the **[Automated Chat History Logging Guide](integration/automated_chat_logging.md)** for configuration details.

## Validation System

The MCP server includes a validation system to objectively measure the quality and impact of code changes. This is particularly useful for qualifying learning promotions with evidence of their effectiveness.

### Setting up Validation Collections

The validation system requires two collections:

- `validation_evidence_v1` - Stores validation evidence like test transitions and error resolutions
- `test_results_v1` - Stores test result data

You can set up these collections with the setup-collections command:

```bash
chroma-mcp-client setup-collections
```

### Collecting Validation Evidence

The validation system supports three types of evidence:

1. **Test Transitions** - Tests that change from failing to passing

    ```bash
    # Log test results
    ./scripts/log_test_results.sh --xml test-results.xml

    # Compare before/after test results
    ./scripts/log_test_results.sh --xml after.xml --before-xml before.xml
    ```

2. **Runtime Error Resolutions** - Errors that are resolved by changes

    ```bash
    # Log a runtime error
    ./scripts/log_error.sh --error-type "TypeError" --message "Cannot read property"

    # Log a resolved error
    ./scripts/log_error.sh --error-type "TypeError" --message "Fixed issue" --resolution "Added null check" --verified
    ```

3. **Code Quality Improvements** - Improvements in code quality metrics

    ```bash
    # Log quality metrics
    ./scripts/log_quality_check.sh --after pylint-output.txt

    # Compare before/after quality metrics
    ./scripts/log_quality_check.sh --before before.txt --after after.txt
    ```

### Validating Evidence

Once you've collected evidence, you can validate it to determine if it meets the promotion threshold:

```bash
# Validate evidence from a file
./scripts/validate_evidence.sh --file evidence.json

# Validate evidence from IDs
./scripts/validate_evidence.sh --test-ids test-123 --runtime-ids error-456
```

### Promoting Validated Learnings

You can use validation evidence when promoting learnings:

```bash
# Promote a learning with validation evidence
chroma-mcp-client promote-learning \
  --description "Use proper null checks to avoid TypeError" \
  --pattern "if (value === null || value === undefined)" \
  --code_ref "src/utils.js:abc123:42" \
  --tags "javascript,error-handling" \
  --confidence 0.95 \
  --require-validation \
  --validation-evidence-id "evidence-123"
```

This ensures that only well-validated learnings are promoted to the derived learnings collection.

## Development

### Development Prerequisites

- Python 3.10+
- `hatch` (Install with `pip install hatch`)
- `just` (optional, for `justfile`)
- `curl`, `jq` (for `release.sh`)

### Setup

```bash
hatch shell # Activate the Hatch environment (installs deps if needed)
cp .cursor/mcp.example.json .cursor/mcp.json
# Edit .cursor/mcp.json and/or .env as needed
```

### Testing

```bash
./scripts/test.sh # Run unit/integration tests
./scripts/test.sh --coverage # Run with coverage

# Build and test local install via uvx
./scripts/test_uvx_install.sh
```

### Releasing

Use the `release.sh` script:

```bash
# Release 0.2.0, install Prod version for local 'uvx chroma-mcp-server' command
./scripts/release.sh 0.2.0

# Release 0.2.1, install Test version for local 'uvx chroma-mcp-server' command
./scripts/release.sh --update-target test 0.2.1
```

## Troubleshooting

- **UVX Cache Issues:** If `uvx` seems stuck on an old version, try refreshing its cache: `uvx --refresh chroma-mcp-server --version`
- **Dependency Conflicts:** Ensure your environment matches the required Python version and dependencies in `pyproject.toml`.

## Running the Server

### Standalone Mode (pip/uvx install)

If you installed via `pip` or `uvx`, you can run the server directly. Ensure required environment variables (like `CHROMA_DATA_DIR` for persistent mode, or API keys for specific embedding functions) are set.

```bash
# Run using the installed script
chroma-mcp-server --client-type ephemeral --embedding-function default

# Example with persistent mode (env var set)
# export CHROMA_DATA_DIR=/path/to/data
# chroma-mcp-server --client-type persistent
```

### Via Smithery CLI (Smithery install)

If you installed via Smithery, use the Smithery CLI to run the server. It reads the package's `smithery.yaml` to configure and launch the server locally.

```bash
# Run with default config from smithery.yaml
npx -y @smithery/cli run chroma-mcp-server

# Run with custom configuration override
npx -y @smithery/cli run chroma-mcp-server --config '{ "clientType": "persistent", "dataDir": "./my_smithery_data" }'

# If prompted or required by Smithery configuration, provide a key:
# npx -y @smithery/cli run chroma-mcp-server --key YOUR_API_KEY --config '{...}'
```

### Inspecting via Smithery (Optional)

You can use the Smithery CLI to inspect the server's registered configuration (requires installation via Smithery first):

```bash
npx -y @smithery/cli inspect chroma-mcp-server
```

### Development Mode (Using Hatch)

If you are running from a cloned repository within the development environment, use the provided wrapper script:

```bash
# From the project root directory
./scripts/run_chroma_mcp_server_dev.sh --client-type persistent --data-dir ./dev_data --log-dir ./dev_logs
```

See the [Developer Guide](developer_guide.md#running-the-server-locally) for more details on development setup and running locally.

### Choosing an Embedding Function

The server uses an embedding function to generate vector representations of text for semantic search and other tasks. You can specify which function to use via the `--embedding-function` command-line argument or the `CHROMA_EMBEDDING_FUNCTION` environment variable.

**Available Embedding Functions:**

- `default` / `fast`: Uses `ONNX MiniLM-L6-v2`. Fast and runs locally, good for general use without needing extra setup or API keys. Requires `onnxruntime` (installed by default).
- `accurate`: Uses `all-mpnet-base-v2` via `sentence-transformers`. More accurate but potentially slower than `default`. Requires `sentence-transformers` and `torch`.
- `openai`: Uses OpenAI's embedding models (e.g., `text-embedding-ada-002`). Requires the `openai` package and the `OPENAI_API_KEY` environment variable.
- `cohere`: Uses Cohere's embedding models. Requires the `cohere` package and the `COHERE_API_KEY` environment variable.
- `huggingface`: Uses models from the Hugging Face Hub via the `sentence-transformers` library. Requires `sentence-transformers`, `torch`, and potentially `transformers`. Requires `HUGGINGFACE_API_KEY` if using gated models.
- `voyageai`: Uses Voyage AI's embedding models. Requires the `voyageai` package and the `VOYAGEAI_API_KEY` environment variable.
- `google`: Uses Google's Generative AI embedding models (e.g., Gemini). Requires the `google-generativeai` package and the `GOOGLE_API_KEY` environment variable.
- `bedrock`: Uses embedding models available through AWS Bedrock (e.g., Cohere, Titan). Requires the `boto3` package and configured AWS credentials (via environment variables, shared credential file, or IAM role).
- `ollama`: Uses embedding models served by a local Ollama instance. Requires the `ollama` package and a running Ollama server. The server address can be configured via the `OLLAMA_HOST` environment variable (defaults to `http://localhost:11434`).

**Installation:**

To ensure all dependencies for optional embedding functions like `accurate`, `google`, `bedrock`, `ollama`, `openai`, `cohere`, `voyageai`, and `huggingface` are installed, use the `full` extra:

```bash
pip install "chroma-mcp-server[full]"
```

If you only need the default functions, a simple `pip install chroma-mcp-server` is sufficient.

## Running the Server from terminal

Once installed, you can run the server from your terminal:

```bash
chroma-mcp-server --client-type ephemeral --embedding-function default
```

- `--embedding-function TEXT`: Specifies the embedding function to use. Defaults to `default`. See [Choosing an Embedding Function](#choosing-an-embedding-function) for options.
- `--cpu-execution-provider [auto|true|false]`: Configures ONNX execution provider usage (primarily for `default`/`fast` embedding functions). Defaults to `auto`.
- `--version`: Show the server version and exit.
- `--help`: Show help message and exit.

**Environment Variables:**

Certain arguments can also be set via environment variables:

- `CHROMA_CLIENT_TYPE`: Overrides `--client-type`.
- `CHROMA_DATA_DIR`: Overrides `--data-dir`.
- `CHROMA_HOST`: Overrides `--host`.
- `CHROMA_PORT`: Overrides `--port`.
- `CHROMA_TENANT`: Overrides `--tenant`.
- `CHROMA_DATABASE`: Overrides `--database`.
- `CHROMA_API_KEY`: Overrides `--api-key` (for persistent HTTP/HTTPS clients).
- `CHROMA_EMBEDDING_FUNCTION`: Overrides `--embedding-function`.
- `CHROMA_LOG_DIR`: Overrides `--log-dir`.
- `ONNX_CPU_PROVIDER`: Overrides `--cpu-execution-provider` (true/false).
- `OPENAI_API_KEY`: Required if using `--embedding-function openai`.
- `COHERE_API_KEY`: Required if using `--embedding-function cohere`.
- `HUGGINGFACE_API_KEY`: Required if using `--embedding-function huggingface` with private/gated models.
- `VOYAGEAI_API_KEY`: Required if using `--embedding-function voyageai`.
- `GOOGLE_API_KEY`: Required if using `--embedding-function google`.
- `OLLAMA_HOST`: Specifies the Ollama server address (e.g., `http://host.docker.internal:11434`) if using `--embedding-function ollama`. Defaults to `http://localhost:11434`.
- AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION`, etc.): Required if using `--embedding-function bedrock` and not configured via other means (e.g., IAM role, shared credential file).

## Docker

Build and run via Docker:

```bash
docker build -t chroma-mcp-server .
docker run -p 8000:8000 \
  -e CHROMA_CLIENT_TYPE=persistent \
  -e CHROMA_DATA_DIR=/data \
  -e CHROMA_LOG_DIR=/logs \
  -e CHROMA_EMBEDDING_FUNCTION=default \
  chroma-mcp-server
```

Or with Compose:

```bash
docker-compose up --build
```

### Server Logging

The server logs output in several ways depending on the mode of operation:

- **Stdio Mode** (default for MCP servers like Cursor integration): All Python logging is redirected to dedicated per-execution log files (e.g., `logs/chroma_mcp_stdio_<timestamp>.log`) to prevent contamination of the JSON communication stream.
- **HTTP Mode**: Standard Python logging to console and optionally to log files.

Log levels and directories are configurable through environment variables. See the [Server Logging Guide](logging/server_logging.md) for comprehensive details about the logging system improvements.
