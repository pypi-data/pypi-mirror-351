# Action Plan v4: Evolvable Local RAG to Reinforcement Learning Pipeline

**Purpose:** Provide a seamless and forward-compatible plan to evolve from a simple local RAG setup (no fine-tuning) toward a full reinforcement learning + model fine-tuning (LoRA) workflow – without breaking ChromaDB collections or needing to reindex existing code or chat history. This plan allows individual developers or teams to start at any phase and progressively adopt more advanced features.

**Core Architecture (Consistent Across Phases):**

- **ChromaDB:** Vector database for storing code chunks, chat summaries, and derived learnings. Can be local (SQLite-backed) or a shared server instance.
- **Automation (Git Hooks, CI, Scripts):** Uses dedicated Python client modules (`src/chroma_mcp_client/`) exposed via installable console scripts (e.g., `chroma-mcp-client`) that connect *directly* to the ChromaDB backend based on `.env` configuration.
- **Interaction (IDE - Cursor, Windsurf, etc.):** Leverages the `chroma-mcp-server` running via IDE's MCP integration. The server facilitates working memory tools and automated logging of summarized prompt/response pairs to `chat_history_v1`.
- **Learning Extraction & Application:** Processes evolve from manual analysis to automated pipelines that identify valuable interactions, train models, and feed insights back into the RAG system.

**Important Development Workflow Notes (Applies to all phases):**

- **Rebuild & Reinstall after Changes:** After modifying the `chroma-mcp-server` codebase (including client or thinking modules), you **must** rebuild and reinstall the package within the Hatch environment:

  ```bash
  hatch build && hatch run pip uninstall chroma-mcp-server -y && hatch run pip install 'dist/chroma_mcp_server-<version>-py3-none-any.whl[full,dev]'
  ```

- **Run Tests After Updates:** Always run unit tests after code changes and reinstalling:

  ```bash
  ./scripts/test.sh -c -v
  ```

---

## Overview of Evolution Phases

| Phase | Description                                                           | Core Chroma Collections Used                                 | Key Requirements                                                                 | Compatible with Next Phase? |
| ----- | --------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------- | --------------------------- |
| **1** | Local RAG-Only (Implicit Learning via Chat History)                   | `codebase_v1`, `chat_history_v1`, `derived_learnings_v1`     | ChromaDB (local/shared), IDE + Git + MCP Rules, `chroma-mcp-client` CLI              | ✅ Yes                       |
| **2** | RAG + LoRA Fine-Tuning (Manual/Optional)                              | (Same as Phase 1)                                            | Adds reward dataset export, manual LoRA adapter training, optional adapter use   | ✅ Yes                       |
| **3** | Full RL Pipeline: Nightly Analysis, Automated Training, LoRA Deployment | (Same as Phase 1, enriched metadata)                         | Adds scheduling, auto-promotion, CI/CD ops, potentially shared ChromaDB for team | ✅ Yes                       |

---

## Phase 1: Local RAG-Only (Implicit Learning & Enhanced Context Capture)

**Goal:** Establish a robust local RAG system with automated codebase indexing, rich contextual chat history logging, bi-directional linking between code and conversations, and a semi-automated mechanism for curating high-quality "derived learnings".

**Collections Used & Schema Definition:**

- `codebase_v1`: Indexed code chunks from the repository.
  - [X] Ensure schema includes `file_path`, `commit_sha`, `chunk_id`, timestamps, etc. (Partially from v3 [~] 4.1, expanded for v4, in particular for `chunk_id` and `commit_sha`)
  - [X] **Add new fields:** `related_chat_ids` (comma-separated list of `chat_history_v1` entry IDs that modified this code)
- `chat_history_v1`: Summarized AI prompt/response pairs with rich context.
  - [X] Create collection using MCP client (`#chroma_create_collection`).
  - [X] **Define and fully implement required metadata structure:** `session_id`, `timestamp`, `prompt_summary`, `response_summary`, `involved_entities`, `raw_prompt_hash`, `raw_response_hash`, and `status` (e.g., `captured`, `analyzed`, `promoted_to_learning`, `exported_for_reward`, `rewarded_implemented`, `ignored_not_implemented`). (Partially from v3 [~] 4.1, expanded for v4)
  - [X] **Add enhanced context fields:** `code_context` (before/after code snippets), `diff_summary` (key changes made), `tool_sequence` (e.g., "read_file→edit_file→run_terminal_cmd"), `modification_type` (refactor/bugfix/feature/documentation), and `confidence_score` (AI-assessed value from 0.0-1.0)
- `derived_learnings_v1`: Manually validated and promoted insights.
  - [X] **Define and implement schema:** `learning_id` (UUID string), `source_chat_id` (optional string FK to `chat_history_v1`), `description` (document content), `pattern` (string), `example_code_reference` (chunk_id string from `codebase_v1`), `tags` (comma-sep string), `confidence` (float).
  - [X] **Create collection using MCP client or `chroma-mcp-client`.**
- `thinking_sessions_v1`: For working memory.
  - [X] Create collection using MCP client.

**Key Features & Workflow Implementation:**

1. **Setup & Configuration (Common Components):**
    - [X] Install prerequisites (Python, Git, `chroma-mcp-server[full,client,dev]`).
    - [X] Prepare shared `.env` for ChromaDB connection (local path or server URL), API keys, embedding model choice (handling both local persistent and remote HTTP ChromaDB configs).
    - [X] Setup client modules (`src/chroma_mcp_client/`), packaging (`pyproject.toml`).
    - [X] Implement and configure unit tests (pytest, mock, coverage, etc.).
    - [X] Ensure `chroma-mcp-server` is launchable via IDE / `python -m chroma_mcp.cli`.
    - [X] Implement `chroma-mcp-client` console script for CLI operations and wrapper scripts (`scripts/*.sh`).
    - [X] **Implement `chroma-mcp-client setup-collections` command to check and create all required collections (`codebase_v1`, `chat_history_v1`, `derived_learnings_v1`, `thinking_sessions_v1`, `test_results_v1`) if they don't exist.**
    - [X] Verify direct client connection (HTTP/Cloud via console script).
    - [X] Ensure security & secrets checklist followed (`.env` gitignored, etc.).
    - [X] Add comprehensive unit tests for client logic (`tests/client/`, etc., 80% coverage).

2. **Codebase Indexing with Contextual Chunking:**
    - [X] Ensure `codebase_v1` collection exists/is created by client.
    - [X] `chroma-mcp-client index --all`: Initial full codebase indexing into `codebase_v1`.
    - [X] Git `post-commit` hook using `chroma-mcp-client index --changed` for incremental updates.
    - [X] Implement basic query interface (`chroma-mcp-client query`).
    - [X] **Enhance the chunking strategy to use semantic boundaries (function/class definitions, logical sections) instead of fixed-size chunks.**
    - [X] **Update indexing to support bi-directional linking by tracking which chat sessions modify which code files.**

3. **Enhanced Interactive RAG & Rich Chat Logging (IDE Integration):**
    - [X] IDE connects to `chroma-mcp-server`.
    - [X] AI Assistant uses `chroma_query_documents` (MCP tool) to retrieve context from `codebase_v1`.
    - [X] **Refine `chroma_query_documents` (MCP tool) to also query `derived_learnings_v1` (mixed query or separate, with weighting).** (v3 [ ] 4.6)
    - [X] **Automated Chat Capture:** IDE rule (`auto_log_chat`) for summarizing prompt/response and logging to `chat_history_v1` via `#chroma_add_document_with_metadata`.
    - [X] **Enhance the `auto_log_chat` rule to:**
      - [X] **Extract code context (before/after snippets) when edits are made**
      - [X] **Generate diff summaries for code modifications**
      - [X] **Track tool usage sequences (e.g., read_file→edit_file→run_terminal_cmd)**
      - [X] **Assign confidence scores during creation to help identify valuable interactions**
      - [X] **Categorize interactions (refactor/bugfix/feature/documentation)**
      - [X] **Store enriched contextual information in the document and metadata**

4. **Working Memory (Sequential Thinking):**
    - [X] `record-thought` console script logs to `thinking_sessions_v1`.
    - [X] Implement sequential thinking logic in `src/chroma_mcp_thinking/`.
    - [X] IDE integration (`memory-integration-rule`) allows AI to query `chroma_find_similar_thoughts`.
    - [X] Add unit tests for thinking logic (`tests/thinking/`).

5. **Enhanced Implicit Learning Analysis & Semi-Automated Promotion:**
    - [X] `analyze-chat-history` (CLI subcommand) fetches `captured` entries from `chat_history_v1`, correlates with code changes, updates status to `analyzed`.
    - [X] **Implement `promote-learning` CLI subcommand or define a robust manual process to create entries in `derived_learnings_v1` from `analyzed` chat history or other sources.**
    - [X] **Ensure `promote-learning` process updates the status of source `chat_history_v1` entries to `promoted_to_learning`.**
    - [X] **Integrate analysis and promotion steps into a documented developer workflow (initially manual execution).** (v3 [ ] 4.5)
    - [X] **Manual Promotion Workflow:** Implement `promote-learning` command.
    - [X] **Interactive Promotion Workflow:** Implement `review-and-promote` command. (Provides interactive review, codebase search for code refs, calls refactored promotion logic, and includes robust error handling for embedding function mismatches).
    - [X] **Enhance `analyze-chat-history` to:**
      - [X] **Leverage the new rich context fields to identify high-value interactions**
      - [X] **Use confidence scores to prioritize entries for review**
      - [X] **Flag interactions that have significant code impact based on diff analysis**
    - [X] **Improve `review-and-promote` to implement a streamlined approval interface for candidate learnings.**

**Phase 1 Verification:**

- [X] End-to-End Test (Automation: Git hook for `codebase_v1` indexing).
- [X] **End-to-End Test (Interaction & Logging: IDE -> MCP Server -> RAG from `codebase_v1` & `derived_learnings_v1` -> AI response -> AI logs to `chat_history_v1`).** (Adapted from v3 [ ] 7.2)
- [X] End-to-End Test (Working Memory: `record-thought` via CLI/IDE task).
- [X] **Test `analyze-chat-history` command thoroughly.** (Adapted from v3 [ ] 7.4)
- [X] **Test `promote-learning` workflow and `derived_learnings_v1` creation.**
- [X] Test All Console Scripts (`chroma-mcp-client` subcommands, `record-thought`).
- [X] Run All Unit Tests (maintain >=80% coverage).
- [X] **Quality Assessment:** Periodically evaluate usefulness/accuracy of `derived_learnings_v1` entries.
- [X] **Test enhanced context capture in `auto_log_chat` rule.**
- [X] **Verify bi-directional links between code and chat history.**

**Forward Compatibility:** ✅ Fully forward-compatible with Phase 2. No schema changes required for existing collections. New metadata fields are additive and non-breaking.

---

## Phase 2: RAG + LoRA Fine-Tuning (Optional & Manual)

**Goal:** Enable developers to optionally fine-tune a LoRA adapter using validated learnings, and apply this adapter on-demand within their IDE.

**Additions to Phase 1 (New Collections/Files - External to ChromaDB):**

- `rl_dataset_YYYYMMDD.jsonl`: Exported reward dataset.
- `lora_codelearn_YYYYMMDD.safetensors`: Trained LoRA adapter file.

**Workflow Changes & Implementation:**

1. **Export Reward Dataset:**
    - [ ] **Develop `chroma-mcp-client export-rl-dataset` command.**
    - [ ] **Define the schema for `rl_dataset_YYYYMMDD.jsonl` (e.g., prompt-completion pairs).**
    - [ ] **Implement logic in `export-rl-dataset` to extract and transform data from `chat_history_v1` (status `promoted_to_learning` or `rewarded_implemented`) or `derived_learnings_v1`.**
    - [ ] **Ensure `chat_history_v1` entries used are marked with status `exported_for_reward`.**

2. **Manual LoRA Fine-Tuning:**
    - [ ] **Provide an example `scripts/train_lora.sh` (wrapper for a fine-tuning framework like `lit-gpt`, `axolotl`, etc.).**
    - [ ] **Document the manual LoRA fine-tuning process using the exported dataset.**

3. **On-Demand Adapter Usage in IDE:**
    - [ ] **Investigate and document how to load and use LoRA adapters on-demand with target LLMs/IDEs.**
    - [ ] (Optional) Implement any necessary MCP tools or IDE commands if dynamic loading needs server assistance.

**Phase 2 Verification:**

- [ ] **Test `chroma-mcp-client export-rl-dataset` command and the format of `rl_dataset.jsonl`.**
- [ ] **Manually train a sample LoRA adapter using an exported dataset.**
- [ ] **Test on-demand usage of the trained LoRA adapter in an IDE setup and evaluate its impact.**
- [ ] Cost Check: Monitor API costs if using paid models for fine-tuning or inference. (v3 [ ] 7.7)

**ChromaDB Compatibility:** ✅ `codebase_v1`, `chat_history_v1`, `derived_learnings_v1` schemas are unchanged. New additive `status` values in `chat_history_v1` are non-breaking.

---

## Phase 3: Full Reinforcement Learning Pipeline (Automated & Scheduled)

**Goal:** Automate the analysis, reward dataset generation, LoRA training, and adapter deployment processes, creating a continuous learning loop, ideally with a shared ChromaDB.

**Additions to Phase 2 (Automation & Scripts):**

- `scripts/nightly_analysis.sh`: Automates `analyze-chat-history` and potentially `export-rl-dataset`.
- `scripts/retrain_lora_incrementally.sh`: Automates LoRA training.
- `scripts/deploy_adapter.sh`: Automates LoRA adapter deployment.

**Automation Layers & Workflow Implementation:**

1. **Automated Chat History Tagging & Reward Signal Generation:**
    - [ ] **Enhance `analyze-chat-history` script for more robust correlation (e.g., AST changes, specific code patterns) to automatically tag `chat_history_v1` entries with statuses like `rewarded_implemented` or `ignored_not_implemented`.**
    - [ ] **Ensure the automated `export-rl-dataset` (called by `nightly_analysis.sh`) uses these refined statuses.**

2. **Scheduled LoRA Retraining:**
    - [ ] **Develop `scripts/nightly_analysis.sh` to run data preparation tasks.**
    - [ ] **Develop `scripts/retrain_lora_incrementally.sh` for automated, scheduled LoRA training.**
    - [ ] **Implement LoRA adapter versioning (e.g., `lora_codelearn_YYYY-MM-DD.safetensors`).**
    - [ ] **Document setup for scheduled jobs (e.g., cron).**

3. **Automated Adapter Deployment/Rotation:**
    - [ ] **Develop `scripts/deploy_adapter.sh` to manage LoRA adapter deployment/availability (e.g., copy to shared location, update config).**
    - [ ] **Define and implement a strategy for selecting/distributing the active LoRA adapter for IDEs/models.**

4. **CI/CD Optional Enhancements (Primarily for Shared ChromaDB):**
    - [ ] (Optional) **Merge Gate:** CI checks if new code adheres to patterns found in `derived_learnings_v1`.
    - [ ] (Optional) **Automated Diff Validation:** AI (potentially using the latest LoRA) reviews PRs.
    - [ ] (Optional) **Document setup for Team Learning Aggregation with a shared ChromaDB instance.**

**Phase 3 Verification:**

- [ ] **Test the full automated pipeline: `nightly_analysis.sh` -> `retrain_lora_incrementally.sh` -> `deploy_adapter.sh`.**
- [ ] **Verify LoRA adapter versioning and correct deployment of the latest adapter.**
- [ ] **Evaluate the quality and impact of automatically trained and deployed LoRA adapters over time.**
- [ ] Latency Benchmark: Measure interactive query latency with automatically updated LoRAs. (v3 [ ] 7.9 adapted)

**ChromaDB Compatibility:** ✅ Existing collections remain compatible. Metadata enrichments are non-breaking.

---

## Collection Compatibility Matrix

| Collection                     | Phase 1 | Phase 2 | Phase 3 | Notes                                                                 |
| ------------------------------ | ------- | ------- | ------- | --------------------------------------------------------------------- |
| `codebase_v1`                  | ✅       | ✅       | ✅       | Static chunks + metadata                                              |
| `chat_history_v1`              | ✅       | ✅       | ✅       | New statuses/metadata non-breaking (e.g., `rewarded`, `ignored`)      |
| `derived_learnings_v1`         | ✅       | ✅       | ✅       | Learning pattern stable; new optional fields non-breaking             |
| `thinking_sessions_v1`         | ✅       | ✅       | ✅       | For working memory, largely independent of RL cycle                   |
| `test_results_v1`              | ✅       | ✅       | ✅       | For tracking test execution results and quality metrics               |
| `rl_dataset_*.jsonl`           | ❌       | ✅       | ✅       | Export-only format, external to ChromaDB                            |
| `lora_codelearn_*.safetensors` | ❌       | ✅       | ✅       | Trained model adapter, external to ChromaDB                         |

---

## CLI & Tooling Compatibility

| Script/Command                 | Phase 1                    | Phase 2                    | Phase 3                        | Notes                                                       |
| ------------------------------ | -------------------------- | -------------------------- | ------------------------------ | ----------------------------------------------------------- |
| `chroma-mcp-client index`          | ✅                          | ✅                          | ✅                              | Core indexing                                               |
| `chroma-mcp-client query`          | ✅                          | ✅                          | ✅                              | Core querying (may evolve to use LoRA contextually)         |
| `chroma-mcp-client analyze-chat-history` | ✅ (manual trigger)         | ✅ (manual trigger)         | ✅ (automated, enhanced)       | Analyzes chat for learning signals                        |
| `chroma-mcp-client promote-learning` | ✅ (manual)                 | ✅ (manual)                 | ✅ (manual, or semi-automated) | Curates `derived_learnings_v1`                            |
| `chroma-mcp-client log-test-results` | ✅ (manual/CI integration)   | ✅ (manual/CI integration)   | ✅ (automated)                 | Stores and analyzes test execution results                 |
| `record-thought`               | ✅                          | ✅                          | ✅                              | For working memory                                          |
| `chroma-mcp-client export-rl-dataset` | ❌                          | ✅ (manual trigger)         | ✅ (automated)                 | Creates fine-tuning dataset                               |
| `scripts/train_lora.sh`        | ❌                          | ✅ (manual execution)       | ✅ (automated)                 | Wrapper for LoRA training                                   |
| `scripts/deploy_adapter.sh`    | ❌                          | ❌                          | ✅ (automated)                 | Manages LoRA adapter deployment                             |
| `official-client log-chat`     | ✅ (refined implementation)  | ✅ (refined implementation)  | ✅ (refined implementation)     | Manually logs chat interactions with enhanced context      |
| Official `chroma` CLI          | ✅ (for DB admin)           | ✅ (for DB admin)           | ✅ (for DB admin)              | For tasks like `copy`, `vacuum`, server management          |

---

## Design Guarantee: Forward Compatibility

All transitions (Phase 1 → 2 → 3) are designed to be **non-breaking**.

- **No Re-indexing Required:** Existing data in `codebase_v1`, `chat_history_v1`, etc., remains valid.
- **Stable Core Schemas:** Core fields in collections are preserved. New metadata fields are additive and optional.
- **No Destructive Migrations:** Upgrades do not require deleting or rebuilding ChromaDB collections from scratch.

Developers can adopt advanced phases incrementally without losing prior work or data.

---

## Data Migration & ChromaDB Management (Local to Shared)

For individual use, a local ChromaDB (SQLite-backed, configured via `CHROMA_DB_PATH` in `.env`) is sufficient for Phases 1 and 2. Phase 3, especially with team-based learning and CI/CD integration, benefits significantly from a **shared ChromaDB server instance**.

**Implementation & Documentation Tasks:**

1. **Official Chroma CLI Usage:**
    - [X] Ensure official `chroma` CLI is installable/accessible by developers.
    - [ ] **Document usage of `chroma copy` for migrating `codebase_v1`, `chat_history_v1`, `derived_learnings_v1`, `thinking_sessions_v1` between local and shared instances.**
    - [ ] **Document usage of `chroma utils vacuum --path <your-data-directory>` for local DB optimization prior to backup/migration.** (Requires server shutdown).

2. **Backup for Local ChromaDB:**
    - [ ] **Adapt `scripts/backup_chroma.sh` for robust local filesystem backups of all relevant ChromaDB data directories (e.g., `CHROMA_DB_PATH`).** (Adapted from v3 [ ] 6.7)
    - [ ] Document procedure for stopping server/client processes before backup.

3. **Shared Server Management:**
    - [ ] Provide guidance/links to documentation for backup/maintenance of shared ChromaDB server instances (Docker, Kubernetes, Chroma Cloud).

**Verification:**

- [ ] **Test Restore-from-Backup for all relevant local ChromaDB collections using the `backup_chroma.sh` script and manual copy.** (v3 [ ] 7.11)
- [ ] **Perform a test migration of all collections from a local instance to another local instance (simulating server migration) using `chroma copy`.**

---

## Shared Configuration (`.env`) Updates for Phases

Your `.env` file will need to accommodate different ChromaDB backend configurations:

```dotenv
# --- ChromaDB Configuration ---
# For local persistent DB (Phases 1, 2, or local Phase 3)
CHROMA_DB_IMPL="persistent"
CHROMA_DB_PATH="./data/chroma_db" # Or any other local path

# For remote/shared ChromaDB server (Recommended for collaborative Phase 3)
# CHROMA_DB_IMPL="http"
# CHROMA_HTTP_URL="http://your-chroma-server-address:8000"
# CHROMA_HTTP_HEADERS="" # e.g., "Authorization: Bearer your_token" if auth is enabled

# --- Embedding Model ---
# EMBEDDING_MODEL_PROVIDER="default" # or "openai", "huggingface_hub", "vertex_ai"
# EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2" # if using default or hf
# OPENAI_API_KEY="sk-..." # if using openai
# HF_TOKEN="hf_..." # if using hf for private models
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcp-credentials.json" # if using Vertex AI

# --- Other configurations ---
LOG_LEVEL="INFO"
# ... any other relevant settings
```

- [X] Ensure `.env` is in `.gitignore`.
- [ ] (Optional) **Implement and document support for custom embedding functions configured via `.env`.** (v3 [ ] 6.6)

---

## Optional Enhancements (Consider for any Phase)

- [ ] (Optional) **Add `repo_id` to metadata in all relevant collections for multi-repository setups.**
- [ ] **Enrich `derived_learnings_v1` schema further with `tags`, `category` (for filtering/organization).**
- [ ] **Track `model_version` (base model and any active LoRA) in `chat_history_v1` metadata.**
- [ ] (Optional) **Implement more sophisticated performance/cost tuning measures (chunking strategies, quantization).** (v3 [ ] 6.2)
- [ ] **Setup basic monitoring and logging for server and client operations.** (v3 [ ] 6.3)
- [x] **Implement automatic log rotation to remove log files older than the specified retention period (default 7 days).**
- [ ] (Optional) **Implement HTTP resilience & retries in client if using HTTP/Cloud backend.** (v3 [ ] 6.4)
- [ ] **Investigate/Setup Observability / Metrics Dashboard for key pipeline metrics.** (v3 [ ] 6.5)
- [ ] **Add action-oriented tagging with structured categories like refactoring, bug fixing, feature implementation, documentation.**
- [ ] (Optional) **Implement session context enrichment to better group related interactions across multiple chat exchanges.**
- [ ] (Optional) **Create a visualization tool for navigating the connections between code changes and chat history.**
- [ ] (Optional) **Add support for multimedia content in chat summaries (e.g., screenshots, diagrams) to enhance context.**
- [ ] **Upgrade existing CLI tools (`analyze_chat_history.sh`, `promote_learning.sh`, `review_and_promote.sh`) to fully leverage enhanced metadata captured by the logging system for better context awareness and correlation.**
- [x] **Rename CLI executable from `chroma-client` to `chroma-mcp-client` for naming consistency as outlined in [client_rename_plan.md](./client_rename_plan.md).**
- [x] **Update test script to use new test artifact locations as outlined in [test_artifacts_organization_plan.md](./test_artifacts_organization_plan.md).**
- [x] **Migrate all shell scripts to Python modules as outlined in [shell_script_migration_plan.md](./shell_script_migration_plan.md).**

---

## Enhanced Test Result Integration

**Goal:** Establish a structured system for capturing, storing, and analyzing test results to measure code quality improvements and correlate them with RAG-assisted development.

**Collections Used & Schema Considerations:**

- `test_results_v1`: A new collection for storing test execution results.
  - [X] **Define and implement schema:** `test_run_id` (UUID string), `timestamp`, `test_file` (path to test file), `test_name`, `status` (pass/fail/skip), `duration` (seconds), `error_message` (for failures), `stacktrace` (for debugging), `related_chat_ids` (comma-separated list linking to discussions), `related_code_chunks` (comma-separated chunk_ids from `codebase_v1`).
  - [ ] **Alternative approach:** Extend `chat_history_v1` schema with test result metadata for direct correlation.

**Implementation Tasks:**

1. **Test Execution Result Capture:**
   - [X] **Modify hatch-test environment scripts to generate and store structured test results (replacing test.sh)**
     - [X] Add `--junitxml=test-results.xml` parameter to pytest call
     - [X] Implement parsing of JUnit XML to extract structured test data (in `test_collector.py`)
     - [ ] Track pass/fail counts, execution times, and specific test failures over time
     - [ ] Track correlation with git commits via commit hash tracking

2. **Results Storage and Integration:**
   - [X] **Implement `log-test-results` functionality in chroma-mcp-client**
     - [X] Store results in new `test_results_v1` collection or extend `chat_history_v1`
     - [ ] Include bi-directional links to related code chunks and chat sessions
     - [ ] Track correlation between test failures and subsequent fixes
     - [ ] Implement metrics calculation (pass rate, flakiness score, coverage trends)

3. **RAG Enhancement with Test Awareness:**
   - [ ] **Add test history context to code chunks in `codebase_v1`**
     - [ ] Include test success/failure history in code context
     - [ ] Track which tests cover which code chunks
     - [ ] Prioritize patterns that resolved recurring test failures
     - [ ] Create derived learnings from successful test fixes with high impact

4. **Quality Measurement:**
   - [X] **Develop metrics for measuring RAG impact on testing**
     - [X] Track reduction in test failures after RAG implementation
     - [ ] Measure time-to-fix for failing tests with/without RAG assistance
     - [ ] Calculate complexity reduction in test implementations
     - [ ] Analyze test coverage improvements correlating with RAG usage

**Verification Tasks:**

- [X] **Create unit tests for the test result parser**
- [ ] **Test the end-to-end flow from test execution to result storage**
- [ ] **Verify bi-directional linking between test results, code, and chat history**
- [ ] **Create baseline measurements for pre-RAG test metrics**
- [ ] **Implement a reporting mechanism for test quality trends**

**Integration with Current RAG Workflow:**

- [ ] **Update documentation to include test result tracking in developer workflow**
- [ ] **Create guidelines for interpreting test metrics in context of RAG improvements**
- [ ] **Establish process for periodic review of test trends and correlation with derived learnings**

## Enhanced Error-Driven Learning Integration

**Goal:** Extend the test-based validation system to include runtime errors and create a comprehensive validation framework for promoting only evidence-based learnings.

**Implementation Tasks:**

1. **Runtime Error Logging:**
   - [X] **Implement mechanism for capturing runtime errors**
     - [X] Create a Python decorator/context manager for logging errors to ChromaDB
     - [X] Build integration hooks for common error handlers/loggers
     - [X] Develop CLI command to import error logs from external sources
   - [X] **Design runtime error schema**
     - [X] Error type, message, stacktrace
     - [X] Context (user action, environment, input data)
     - [X] Affected code chunks (bidirectional linking)
     - [X] Resolution status

2. **Error-Resolution Tracking:**
   - [X] **Implement tracking of error resolution lifecycle**
     - [X] Initial error occurrence
     - [X] Associated discussions (chat_history_v1 entries)
     - [X] Code changes made to address error
     - [X] Verification of resolution
   - [X] **Create bidirectional links between errors and fixes**
     - [X] Link errors to code chunks that caused them
     - [X] Link fixed code to the errors it resolved
     - [X] Create metrics for error resolution effectiveness

3. **Validation Evidence Collection:**
   - [X] **Implement validation scoring system**
     - [X] Define weights for different types of evidence
     - [X] Create scoring algorithm to combine multiple evidence types
     - [X] Set promotion thresholds based on validation scores
   - [X] **Enhance review-and-promote workflow**
     - [X] Display validation evidence during review
     - [X] Filter candidates by validation score
     - [X] Allow on-demand validation during review

4. **Learning Promotion Criteria Update:**
   - [X] **Update `derived_learnings_v1` schema for validation**
     - [X] Add validation_evidence field with structured evidence data
     - [X] Include validation score in metadata
     - [X] Tag learnings by validation type
   - [X] **Modify promotion process**
     - [X] Require validation evidence for promotion
     - [X] Include evidence in promoted learnings
     - [X] Update RAG query to prioritize validated learnings

5. **Integration with Test Results:**
   - [X] **Create unified validation view**
     - [X] Combine test results and runtime errors in validation UI
     - [X] Allow filtering by validation type and score
     - [X] Visualize resolution pathways
   - [X] **Implement verification repository**
     - [X] Store examples that verify learning effectiveness
     - [X] Create regression tests from validated learnings
     - [X] Track long-term impact of promoted learnings

6. **Verification Tasks:**
   - [X] **Create test suite for validation scoring**
   - [X] **Verify proper evidence collection and storage**
   - [X] **Validate promotion criteria effectiveness**
   - [X] **Measure quality of promoted learnings vs. previous approach**
   - [X] **Test git hook preservation with existing codebase indexing functionality**

This error-driven learning integration will transform our derived learnings collection from a repository of arbitrary code changes to a curated collection of validated solutions with proven impact.

---

## ROI Measurement Strategy

**Goal:** Create a comprehensive framework for measuring the return on investment and effectiveness of the RAG implementation with concrete metrics and comparison methods.

**Measurement Areas & Implementation:**

1. **Development Efficiency Metrics:**
   - [ ] **Implement time tracking for development tasks**
     - [ ] Add timestamps to chat history entries for measuring task completion times
     - [ ] Track time between issue identification and resolution
     - [ ] Create comparison baseline between RAG-assisted and non-RAG tasks
   - [ ] **Measure code reuse and pattern application**
     - [ ] Track frequency of derived learning application in new code
     - [ ] Calculate reduction in duplicate solutions across the codebase
     - [ ] Monitor consistency of pattern implementation

2. **Code Quality Impact:**
   - [ ] **Establish quality baseline measurements**
     - [ ] Static analysis metrics (complexity, maintainability index)
     - [ ] Test coverage percentage and distribution
     - [ ] Defect density and severity
   - [ ] **Implement automated before/after comparisons**
     - [ ] Run quality analysis on each commit with reference to previous state
     - [ ] Track quality trend correlations with RAG-assisted development
     - [ ] Generate weekly/monthly quality differential reports

3. **Developer Experience Assessment:**
   - [ ] **Create feedback collection mechanisms**
     - [ ] Add simple feedback prompt after RAG-assisted implementations
     - [ ] Track confidence scores reported by developers
     - [ ] Implement periodic developer surveys on RAG effectiveness
   - [ ] **Analyze learning curve metrics**
     - [ ] Measure time to proficiency for new team members
     - [ ] Track knowledge transfer effectiveness

4. **Business Impact Evaluation:**
   - [ ] **Calculate time-to-market improvements**
     - [ ] Measure feature implementation time with/without RAG assistance
     - [ ] Track reduction in rework/refactoring time
     - [ ] Monitor deployment frequency and stability
   - [ ] **Cost reduction analysis**
     - [ ] Calculate developer time saved by pattern reuse
     - [ ] Measure reduction in technical debt accumulation
     - [ ] Analyze support/maintenance effort reduction

**Integration with Existing Tools:**

- [ ] **Enhance `log-test-results` to include quality metrics**
- [ ] **Add time tracking to chat logging mechanism**
- [ ] **Implement automated quality differential reports tied to git hooks**
- [ ] **Create dashboards showing ROI metrics in the Observability system**

**Periodic Assessment Process:**

- [ ] **Implement monthly ROI review protocol**
- [ ] **Create quarterly trend analysis report template**
- [ ] **Establish continuous feedback loop for improving measurement accuracy**

---

## General Project Documentation & Workflow Refinements

- [X] This document (`local_rag_pipeline_plan_v4.md`) replaces `local_rag_pipeline_plan_v3.md` - **Mark as done once this PR is merged.**
- [X] **Update `README.md`, `developer_guide.md`, IDE integration docs, and specific tool usage docs (e.g., `record-thought.md`) to reflect the v4 phased approach, new CLI commands, and workflows.** (Adapted from v3 [~] 1.11, [~] 5.8, [~] 7.12)
- [X] **Consolidate and update client command documentation (e.g., in `docs/usage/client_commands.md` or `docs/scripts/`) covering all `chroma-mcp-client` subcommands and `record-thought`.** (Adapted from v3 [~] 1.11, [~] 5.8)
- [X] **Create/Update `docs/usage/implicit_learning.md` for Phase 1 implicit learning and analysis workflow.** (v3 [ ] 4.7)
- [X] **Create `docs/usage/derived_learnings.md` detailing the `derived_learnings_v1` schema, its promotion workflow, and how it's used in RAG.**
- [ ] **Create `docs/usage/lora_finetuning.md` for Phase 2 manual LoRA process and on-demand usage.**
- [ ] **Create `docs/usage/automated_rl_pipeline.md` for Phase 3 automated training and deployment.**
- [X] **Review and update Working Memory documentation (`docs/thinking_tools/`, `docs/scripts/record-thought.md`), including specific workflow checkpoints/usage patterns.** (Adapted from v3 [~] 5.4, [~] 5.8)
- [ ] **Define and document an overall prompting strategy that incorporates RAG from multiple sources (`codebase_v1`, `derived_learnings_v1`), working memory, and conditionally LoRA-adapted models.** (v3 [ ] 6.1)
- [X] **Verify all user-facing scripts are executable and have clear usage instructions.**
- [ ] **Index Size & Storage Check:** Document how to monitor data directory sizes and provide guidance on managing them. (v3 [ ] 7.10)
- [X] **Create `docs/usage/enhanced_context_capture.md` explaining the enriched chat logging system and bi-directional linking.**
- [X] **Update `docs/rules/auto_log_chat.md` with new code snippet extraction and tool sequence tracking functionality.**
- [X] **Add section to developer guide on effective use of confidence scores and action-oriented tagging.**
- [X] **Develop troubleshooting guide for common issues with the enhanced context capture system.**
- [X] **Create `docs/usage/test_result_integration.md` explaining the test result tracking system and its integration with the RAG workflow.**
- [X] **Update Testing and Build Guide to include JUnit XML output and result logging for hatch-test environment scripts.**
- [X] **Add section to developer guide on interpreting test metrics and correlating them with RAG effectiveness.**
- [X] **Create `docs/usage/automated_test_workflow.md` documenting the automated test-driven learning workflow, setup, and usage.**
- [X] **Update `.cursorrules` document with guidance for the `--auto-capture-workflow` flag.**
- [X] **Update `.windsurfrules` document with guidance for the `--auto-capture-workflow` flag.**
- [X] **Update `.github/.copilot-instructions.md` document with guidance for the `--auto-capture-workflow` flag.**
- [ ] **Create `docs/usage/roi_measurement.md` documenting the metrics, tools, and processes for measuring RAG effectiveness.**

---

*Next Steps after this plan is adopted:*

- Prioritize implementation of remaining unchecked items for Phase 1, focusing on `derived_learnings_v1`.
- Begin development of `export-rl-dataset` for Phase 2.
- Plan detailed architecture for automation scripts and shared DB considerations for Phase 3.

*Implementation Priorities for Enhanced Context Capture:*

1. **Update `auto_log_chat` Rule First:** ✅
   - Implement code snippet extraction and diff generation
   - Add tool sequence tracking
   - Incorporate confidence scoring mechanism
   - This captures the richest information at the moment of creation

2. **Create Context Capture Module:** ✅
   - Create `src/chroma_mcp_client/context.py` for reusable context extraction logic
   - Implement functions for:
     - Code snippet extraction from before/after edits
     - Diff generation and summarization
     - Tool sequence tracking and pattern recognition
     - Confidence score calculation
     - Bidirectional link management
   - Add comprehensive documentation and examples
   - This module will be used by the enhanced `auto_log_chat` rule and potentially other tools

3. **Update Collection Schemas:** ✅
   - Enhance `chat_history_v1` schema with new context fields
   - Add bidirectional linking capabilities to `codebase_v1`

4. **Improve Analysis & Promotion Workflow:** ✅
   - Enhance `analyze-chat-history` to use new context fields
   - Update `review-and-promote` with streamlined candidate approval
   - Develop better visualization of connections between code and discussions

5. **Improve Contextual Chunking:** ✅
   - Refine the codebase chunking strategy to use semantic boundaries
   - Update indexing to support the enhanced schema

6. **Complete the CLI integration for validation components**
   - [X] Implement `chroma-mcp-client log-error` command for runtime error logging using our schema
   - [X] Enhance `promote-learning` to leverage validation scores
   - [X] Add `validate-evidence` command for calculating scores on demand
   - [X] Update `analyze-chat-history` to rank entries by validation score

7. **The foundation for validation-driven learning has been established**
   - [X] Core schema definitions for `RuntimeErrorEvidence`, `CodeQualityEvidence`, and `TestTransitionEvidence` are implemented and tested
   - [X] Backward compatibility with older schemas is maintained for smooth transition
   - [X] Validation scoring system with configurable weights per evidence type is operational
   - [X] Test runners can generate structured test data that integrates with the validation system
   - [X] Schema/model compatibility layers handle diverse property names and structure differences

*Refactoring:*

- [X] Promotion logic extracted to `src/chroma_mcp_client/learnings.py` (`promote_to_learnings_collection`).
- [X] Query logic added to `src/chroma_mcp_client/query.py` (`query_codebase`).
- [X] Extract context capture logic to `src/chroma_mcp_client/context.py` for reusability across tools.
- [X] Refactor `auto_log_chat` rule to use the new context capture module.
- [X] Create utility functions for diff generation and code snippet extraction.
- [X] Consider `learning_validation_workflow.md` thoughts into this refactoring plan and update, when necessary to align with the plan.

1. **Test Collection Pipeline:** The `test_collector.py` module now correctly parses JUnit XML output and supports bi-directional linking with code.
2. **Evidence Scoring System:** The `calculate_validation_score` function in schemas.py provides a flexible way to rank learnings by evidence quality.
3. **Schema Compatibility:** All validation evidence types support backward compatibility for smooth migration.

*Testing:*

- [X] Unit tests for `setup-collections`.
- [X] Unit tests for `promote-learning` (covering success, source update, source not found).
- [X] Unit tests for `review-and-promote` interactive script (`test_interactive_promoter.py`).
- [X] Unit tests for `query_codebase` (`test_query.py`), including specific checks for embedding mismatch error handling.
- [X] Unit tests for context capture logic.
- [X] End-to-end tests for enhanced `auto_log_chat` functionality.
- [X] Tests for bidirectional linking between code and chat history.
- [X] Unit tests for validation schemas (RuntimeErrorEvidence, CodeQualityEvidence, TestTransitionEvidence)
- [X] Unit tests for validation scoring system
- [X] Tests for parsing and processing test results
- [X] Unit tests for TestWorkflowManager with comprehensive coverage for setup, failure capture, and transitions
- [X] Unit tests for CLI integration of test workflow commands
- [ ] Integration tests for the complete validation pipeline

*Documentation:*

- [X] Update `docs/scripts/chroma-mcp-client.md` with new commands.
- [X] Update `docs/developer_guide.md` with workflows.
- [X] Update `docs/mcp_test_flow.md` for RAG query changes.
- [X] Update plan doc (this file) with progress.
- [X] Create new documentation for enhanced context capture system.
- [X] Update `auto_log_chat.md` with new code snippet extraction and tool sequence tracking functionality.
- [X] Create API documentation for the context.py module.
- [X] Prepare developer guide for effective use of confidence scores and context extraction.
- [X] Unit tests for validation schemas (RuntimeErrorEvidence, CodeQualityEvidence, TestTransitionEvidence)
- [X] Unit tests for validation scoring system
- [X] Tests for parsing and processing test results
- [X] Unit tests for TestWorkflowManager with comprehensive coverage for setup, failure capture, and transitions
- [X] Unit tests for CLI integration of test workflow commands
- [X] Unit tests for git hook preservation in TestWorkflowManager
- [X] Create comprehensive documentation for the automated test workflow in `docs/usage/automated_test_workflow.md`
- [X] Update `.cursorrules` to include `--auto-capture-workflow` flag guidance
- [X] Update `.windsurfrules` to include `--auto-capture-workflow` flag guidance
- [X] Update `.github/.copilot-instructions.md` to include `--auto-capture-workflow` flag guidance
- [X] Update all relevant documentation to include links to the automated test workflow documentation
- [ ] **Next Steps:** Integration tests for the complete validation pipeline

*Next Immediate Tasks:*

1. [X] Create the skeleton for `src/chroma_mcp_client/context.py` with key function signatures and docstrings
2. [X] Implement the first key function: code snippet extraction
3. [X] Add comprehensive unit tests for context capture logic
4. [X] Begin integrating with auto_log_chat rule once core functionality is stable
5. [X] Implement bidirectional linking between code and chat history
6. [X] Enhance chunking with semantic boundaries
7. [X] **Create `docs/usage/enhanced_context_capture.md` explaining the enriched chat logging system and bi-directional linking.**
8. [X] **Update the review-and-promote workflow to leverage the enhanced context data**
9. [X] **Fix ChromaDB client interaction in auto_log_chat implementation to use proper collection.add() method**
10. [X] **Update tests to correctly mock and verify the ChromaDB client interactions**
11. [ ] **Enhance `analyze_chat_history.sh` to leverage new metadata:**
    - [ ] Prioritize entries with higher confidence scores for analysis
    - [X] Use already-captured code context instead of regenerating git diffs
    - [ ] Leverage tool sequence data for better correlation
    - [ ] Use bidirectional linking information already present
12. [ ] **Improve `promote_learning.sh` to utilize enhanced context:**
    - [ ] Add support for including code context and diffs from source chat entry
    - [X] Use confidence scores to inform default confidence of promoted learnings
    - [ ] Include references to original modification type and tool sequences
    - [ ] Incorporate validation scores from evidence to prioritize promotion candidates
13. [ ] **Enhance `review_and_promote.sh` interface:**
    - [X] Show rich context (code diffs, tool sequences) during review
    - [ ] Sort/prioritize entries by confidence score
    - [ ] Add option to filter by modification type (refactor/bugfix/feature/documentation)
    - [ ] Display linked code chunks via bidirectional linking
    - [X] Show validation evidence and scores for each candidate
14. [ ] **General enhancement task for CLI tools:**
    - [ ] Create a shared module for context rendering to ensure consistent formatting across tools
    - [ ] Implement color coding for diff display in terminal output
    - [ ] Add a "context richness" metric to help prioritize entries with more complete metadata
    - [ ] Create a visual indicator for bidirectional links in CLI interfaces
    - [ ] Add display formatting for validation evidence summary
15. [X] **Initial implementation of test result integration:**
    - [X] Update hatch-test environment scripts to generate JUnit XML output
    - [X] Create the skeleton for test result parser
    - [X] Define schema for test_results_v1 collection
    - [X] Implement basic version of log-test-results command
    - [X] Add unit tests for test result parsing and storage
16. [X] **CLI for the validation pipeline:**
    - [X] Create `chroma-mcp-client log-error` for capturing runtime errors using our schema
    - [X] Add `chroma-mcp-client validate-evidence` for calculating and displaying validation scores
    - [X] Update CLI commands to incorporate evidence-based scoring
    - [X] Add validation reporting options to existing CLI tools
17. [X] **Automate the Test-Driven Learning Workflow:**
    - [X] **Enhance `hatch-test` environment scripts for full automation:**
      - [X] Add `--auto-capture-workflow` flag to `pytest` calls in `pyproject.toml` to enable the automatic test workflow capture pytest plugin.
      - [X] Automatically save failing test results on initial failure (handled by the plugin)
      - [X] Implement git hook integration to detect when tests start passing after edits (part of the plugin and setup command)
    - [X] **Create bidirectional linking with chat history:**
      - [X] Auto-detect which chat sessions influenced code that fixed tests
      - [X] Store references to chat IDs in test results
      - [X] Add test results as evidence in chat history entries
    - [X] **Implement automatic promotion workflow:**
      - [X] Create `setup-test-workflow` command to configure the Git hooks (preserves existing hooks)
      - [X] Create `check-test-transitions` command that identifies high-quality fixes
      - [X] Add configurable threshold for auto-promotion based on validation score
      - [X] Preserve failing→passing transitions with comprehensive context
    - [ ] **Build monitoring dashboard:**
      - [ ] Create CLI view for test transition metrics
      - [ ] Implement quality trend visualization over time
      - [ ] Track correlation between AI assistance and test improvements

18. [X] **Documentation updates for validation:**
    - [X] Update `docs/usage/derived_learnings.md` to include validation scoring information
    - [X] Create `docs/usage/validation_evidence.md` describing the evidence types and scoring system
    - [X] Add schema diagrams showing relationships between evidence types
    - [X] Document the automated test-driven learning workflow in `docs/usage/automated_test_workflow.md`

19. [X] **TestWorkflowManager Enhancements:**
    - [X] Add robust Git hook content preservation to maintain existing functionality
    - [X] Implement automatic correlation between code changes and chat history
    - [X] Add unit tests to verify hook preservation behavior
    - [X] Update CLI integration with proper workspace directory handling
    - [X] Create comprehensive documentation for workflow setup and usage
