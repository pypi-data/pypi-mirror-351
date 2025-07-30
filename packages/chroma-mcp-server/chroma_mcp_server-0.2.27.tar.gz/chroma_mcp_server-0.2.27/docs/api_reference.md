# Chroma MCP Server API Reference

This document provides a detailed reference for the tools and endpoints exposed by the Chroma MCP Server.

**Note on Ongoing Development:** The features and tools listed here are part of an evolving system based on the `docs/refactoring/local_rag_pipeline_plan_v4.md` roadmap. Some tools may be related to features currently under active implementation (Phases 2 and 3).

## Tool Categories

The Chroma MCP Server provides 26 tools across three categories:

1. [Collection Management Tools](#collection-management-tools)
2. [Document Operation Tools](#document-operation-tools)
3. [Sequential Thinking Tools](#sequential-thinking-tools)

---

## Collection Management Tools

### `chroma_create_collection`

Creates a new ChromaDB collection. It is **strongly recommended** to set all desired metadata, including custom keys, description, and specific HNSW parameters, using the `metadata` argument during this initial call, as modifying metadata after creation (especially settings) might be limited or impossible depending on the ChromaDB backend implementation.

#### Parameters for chroma_create_collection

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection to create |
| `metadata` | string | No | Initial collection metadata (including settings) as JSON string |

#### Returns from chroma_create_collection

A JSON object containing basic collection information:

- `name`: Collection name
- `id`: Collection ID
- `metadata`: Initial collection metadata (containing default settings)

#### Example for chroma_create_collection

```json
{
  "collection_name": "my_documents",
  "metadata": {
    "description": "Documents related to project Alpha.",
    "settings": {
      "hnsw:space": "cosine",
      "hnsw:construction_ef": 128,
      "hnsw:search_ef": 64
    }
  }
}
```

### `chroma_list_collections`

Lists all available collections with optional filtering and pagination.

#### Parameters for chroma_list_collections

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit` | integer | No | Maximum number of collections to return (default: 0 = no limit) |
| `offset` | integer | No | Number of collections to skip (default: 0) |
| `name_contains` | string | No | Filter collections by name substring (default: "") |

#### Returns from chroma_list_collections

A JSON object containing:

- `collections`: Array of collection objects
- `total_count`: Total number of collections matching criteria
- `limit`: Applied limit (if specified)
- `offset`: Applied offset (if specified)

#### Example for chroma_list_collections

```json
{
  "limit": 10,
  "offset": 0,
  "name_contains": "doc"
}
```

### `chroma_get_collection`

Gets detailed information about a specific collection.

#### Parameters for chroma_get_collection

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |

#### Returns from chroma_get_collection

A JSON object containing collection details:

- `name`: Collection name
- `id`: Collection ID
- `metadata`: Current collection metadata (including description, settings, and custom keys)
- `count`: Number of documents in the collection
- `sample_entries`: Sample documents from the collection (result of `peek()`)

#### Example for chroma_get_collection

```json
{
  "collection_name": "my_documents"
}
```

### `chroma_rename_collection`

Renames an existing collection.

#### Parameters for chroma_rename_collection

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Current name of the collection |
| `new_name` | string | Yes | New name for the collection |

#### Returns from chroma_rename_collection

A JSON object containing the updated collection information (same as `chroma_get_collection` result, but under the new name).

#### Example for chroma_rename_collection

```json
{
  "collection_name": "my_documents",
  "new_name": "project_alpha_docs"
}
```

### `chroma_delete_collection`

Deletes a collection and all its documents.

#### Parameters for chroma_delete_collection

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection to delete |

#### Returns from chroma_delete_collection

A JSON object with the deletion status.

#### Example for chroma_delete_collection

```json
{
  "collection_name": "my_documents"
}
```

### `chroma_peek_collection`

Gets a sample of documents from a collection.

#### Parameters for chroma_peek_collection

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `limit` | integer | No | Maximum number of documents to return (default: 10) |

#### Returns from chroma_peek_collection

A JSON object containing the peek results:

- `peek_result`: The direct result from ChromaDB's `peek()` method (structure may vary).

#### Example for chroma_peek_collection

```json
{
  "collection_name": "my_documents",
  "limit": 5
}
```

---

## Document Operation Tools

### `chroma_add_document`

Add a document to a collection (auto-generates ID, no metadata).

#### Parameters for chroma_add_document

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection to add the document to. |
| `document` | string | Yes | The document content (string). |
| `increment_index` | boolean | No | Whether to immediately index the added document (default: True). |

#### Returns from chroma_add_document

A JSON object confirming the addition, potentially including the auto-generated ID.

```json
{
  "status": "success",
  "documents_added": 1
}
```

#### Example for chroma_add_document

```json
{
  "collection_name": "my_documents",
  "document": "This is a new document added via single-item tool."
}
```

### `chroma_add_document_with_id`

Add a document with a specified ID to a collection (no metadata).

#### Parameters for chroma_add_document_with_id

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection to add the document to. |
| `document` | string | Yes | The document content (string). |
| `id` | string | Yes | The unique ID for the document. |
| `increment_index` | boolean | No | Whether to immediately index the added document (default: True). |

#### Returns from chroma_add_document_with_id

A JSON object confirming the addition.

```json
{
  "status": "success",
  "documents_added": 1
}
```

#### Example for chroma_add_document_with_id

```json
{
  "collection_name": "my_documents",
  "document": "This document has a specific ID.",
  "id": "doc-manual-id-001"
}
```

### `chroma_add_document_with_metadata`

Add a document with specified metadata to a collection (auto-generates ID).

#### Parameters for chroma_add_document_with_metadata

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection to add the document to. |
| `document` | string | Yes | The document content (string). |
| `metadata` | string | Yes | Metadata JSON string for the document (e.g., '{"key": "value"}'). |
| `increment_index` | boolean | No | Whether to immediately index the added document (default: True). |

#### Returns from chroma_add_document_with_metadata

A JSON object confirming the addition, potentially including the auto-generated ID.

```json
{
  "status": "success",
  "documents_added": 1
}
```

#### Example for chroma_add_document_with_metadata

```json
{
  "collection_name": "my_documents",
  "document": "This document includes metadata.",
  "metadata": "{\"source\": \"api_ref\", \"status\": \"new\"}"
}
```

### `chroma_add_document_with_id_and_metadata`

Add a document with specified ID and metadata to a collection.

#### Parameters for chroma_add_document_with_id_and_metadata

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection to add the document to. |
| `document` | string | Yes | The document content (string). |
| `id` | string | Yes | The unique ID for the document. |
| `metadata` | string | Yes | Metadata JSON string for the document. |
| `increment_index` | boolean | No | Whether to immediately index the added document (default: True). |

#### Returns from chroma_add_document_with_id_and_metadata

A JSON object confirming the addition.

```json
{
  "status": "success",
  "documents_added": 1
}
```

#### Example for chroma_add_document_with_id_and_metadata

```json
{
  "collection_name": "my_documents",
  "document": "This document has ID and metadata.",
  "id": "doc-manual-id-002",
  "metadata": "{\"source\": \"api_ref\", \"status\": \"complete\"}"
}
```

### `chroma_query_documents`

Query documents using semantic search (no filters). Returns IDs and potentially distances/scores.
Use `chroma_get_documents_by_ids` to fetch document details.

#### Parameters for chroma_query_documents

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `query_texts` | array (string) | Yes | List of query strings |
| `n_results` | integer | No | Max results per query (default: 10) |

#### Returns from chroma_query_documents

A JSON object containing the query results, primarily the document IDs.

```json
{
  "ids": [["id1", "id2"]],
  "distances": [[0.5, 0.6]]
}
```

#### Example for chroma_query_documents

```json
{
  "collection_name": "my_documents",
  "query_texts": ["search term"],
  "n_results": 5
}
```

### `chroma_query_documents_with_where_filter`

Query documents using semantic search with a metadata filter. Returns IDs and potentially distances/scores.
Use `chroma_get_documents_by_ids` to fetch document details.

#### Parameters for chroma_query_documents_with_where_filter

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `query_texts` | array (string) | Yes | List of query strings |
| `where` | string | Yes | Metadata filter JSON string |
| `n_results` | integer | No | Max results per query (default: 10) |

#### Returns from chroma_query_documents_with_where_filter

A JSON object containing the filtered query results, primarily the document IDs.

#### Example for chroma_query_documents_with_where_filter

```json
{
  "collection_name": "my_documents",
  "query_texts": ["search term"],
  "where": "{\"source\": \"pdf\"}",
  "n_results": 3
}
```

### `chroma_query_documents_with_document_filter`

Query documents using semantic search with a document content filter. Returns IDs and potentially distances/scores.
Use `chroma_get_documents_by_ids` to fetch document details.

#### Parameters for chroma_query_documents_with_document_filter

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `query_texts` | array (string) | Yes | List of query strings |
| `where_document` | string | Yes | Document content filter JSON string |
| `n_results` | integer | No | Max results per query (default: 10) |

#### Returns from chroma_query_documents_with_document_filter

A JSON object containing the filtered query results, primarily the document IDs.

#### Example for chroma_query_documents_with_document_filter

```json
{
  "collection_name": "my_documents",
  "query_texts": ["search term"],
  "where_document": "{\"$contains\": \"important\"}",
  "n_results": 10
}
```

### `chroma_get_documents_by_ids`

Get document content and metadata from a collection using specific IDs (obtained from a query tool).

#### Parameters for chroma_get_documents_by_ids

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `ids` | array (string) | Yes | List of document IDs to retrieve |

#### Returns from chroma_get_documents_by_ids

A JSON object containing the requested documents, including their IDs, content (`documents`), and `metadatas`.

```json
{
  "ids": ["id1", "id2"],
  "documents": ["content for id1", "content for id2"],
  "metadatas": [{"source": "fileA"}, {"source": "fileB"}]
}
```

#### Example for chroma_get_documents_by_ids

```json
{
  "collection_name": "my_documents",
  "ids": ["id1", "id2", "id3"]
}
```

### `chroma_get_documents_with_where_filter`

Gets documents from a ChromaDB collection using a metadata filter.

**Client Limitation Note:** Some MCP clients may incorrectly serialize optional list parameters (`include`, `limit`, `offset`). If encountering validation errors, try omitting them.

#### Parameters for chroma_get_documents_with_where_filter

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `where` | string | Yes | Metadata filter as JSON string (e.g., '{"source": "pdf"}') |
| `limit` | integer | No | Maximum number of documents (default: 0 = no limit) |
| `offset` | integer | No | Number of documents to skip (default: 0) |
| `include` | array (string) | No | (DEPRECATED) Fields to include |

#### Returns from chroma_get_documents_with_where_filter

A JSON object containing the matching documents.

#### Example for chroma_get_documents_with_where_filter

```json
{
  "collection_name": "my_documents",
  "where": {"source": "api_ref"},
  "limit": 10,
  "include": ["documents", "metadatas"]
}
```

### `chroma_get_documents_with_document_filter`

Gets documents from a ChromaDB collection using a document content filter.

**Client Limitation Note:** Some MCP clients may incorrectly serialize optional list parameters (`include`, `limit`, `offset`). If encountering validation errors, try omitting them.

#### Parameters for chroma_get_documents_with_document_filter

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `where_document` | string | Yes | Document content filter as JSON string |
| `limit` | integer | No | Maximum number of documents (default: 0 = no limit) |
| `offset` | integer | No | Number of documents to skip (default: 0) |
| `include` | array (string) | No | (DEPRECATED) Fields to include |

#### Returns from chroma_get_documents_with_document_filter

A JSON object containing the matching documents.

#### Example for chroma_get_documents_with_document_filter

```json
{
  "collection_name": "my_documents",
  "where_document": {"$contains": "specific ID"},
  "limit": 5,
  "include": ["documents"]
}
```

### `chroma_get_all_documents`

Gets all documents from a ChromaDB collection (use with caution on large collections).

**Client Limitation Note:** Some MCP clients may incorrectly serialize optional list parameters (`include`, `limit`, `offset`). If encountering validation errors, try omitting them.

#### Parameters for chroma_get_all_documents

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `limit` | integer | No | Maximum number of documents |
| `offset` | integer | No | Number of documents to skip |
| `include` | array (string) | No | Fields to include |

#### Returns from chroma_get_all_documents

A JSON object containing all documents (up to the limit).

#### Example for chroma_get_all_documents

```json
{
  "collection_name": "my_documents",
  "limit": 100,
  "include": ["ids", "metadatas"]
}
```

### `chroma_update_document_content`

Updates the content of an existing document by ID.

#### Parameters for chroma_update_document_content

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection containing the document. |
| `id` | string | Yes | The document ID to update. |
| `document` | string | Yes | The new document content. |

#### Returns from chroma_update_document_content

A JSON object confirming the update request.

```json
{
  "status": "success",
  "documents_updated_request": 1
}
```

#### Example for chroma_update_document_content

```json
{
  "collection_name": "my_documents",
  "id": "doc-manual-id-001",
  "document": "Updated content for this specific document."
}
```

### `chroma_update_document_metadata`

Updates the metadata of an existing document by ID.

#### Parameters for chroma_update_document_metadata

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection containing the document. |
| `id` | string | Yes | The document ID to update. |
| `metadata` | string | Yes | New metadata as JSON string (e.g., '{"key": "new_value"}'). |

#### Returns from chroma_update_document_metadata

A JSON object confirming the update request.

```json
{
  "status": "success",
  "documents_updated_request": 1
}
```

#### Example for chroma_update_document_metadata

```json
{
  "collection_name": "my_documents",
  "id": "doc-manual-id-002",
  "metadata": {
    "source": "api_ref",
    "status": "updated",
    "reviewed": true
  }
}
```

### `chroma_delete_document_by_id`

Delete a document from a collection by its specific ID.

#### Parameters for chroma_delete_document_by_id

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection to delete the document from. |
| `id` | string | Yes | The document ID to delete. |

#### Returns from chroma_delete_document_by_id

A JSON object confirming the delete request.

```json
{
  "status": "success",
  "documents_deleted_request": 1
}
```

#### Example for chroma_delete_document_by_id

```json
{
  "collection_name": "my_documents",
  "id": "doc-manual-id-001"
}
```

### `chroma_delete_documents_by_where_filter`

Deletes documents from a ChromaDB collection using a metadata filter.

#### Parameters for chroma_delete_documents_by_where_filter

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `where` | string | Yes | Metadata filter as JSON string to select documents for deletion |

#### Returns from chroma_delete_documents_by_where_filter

A JSON object confirming the request and the filter used.

```json
{
  "status": "success",
  "filter_used": {"source": "obsolete"}
}
```

#### Example for chroma_delete_documents_by_where_filter

```json
{
  "collection_name": "my_documents",
  "where": {"status": "archived"}
}
```

### `chroma_delete_documents_by_document_filter`

Deletes documents from a ChromaDB collection using a document content filter.

#### Parameters for chroma_delete_documents_by_document_filter

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `collection_name` | string | Yes | Name of the collection |
| `where_document` | string | Yes | Document content filter as JSON string for deletion |

#### Returns from chroma_delete_documents_by_document_filter

A JSON object confirming the request and the filter used.

```json
{
  "status": "success",
  "filter_used": {"$contains": "temporary"}
}
```

#### Example for chroma_delete_documents_by_document_filter

```json
{
  "collection_name": "my_documents",
  "where_document": {"$contains": "old project data"}
}
```

---

## Sequential Thinking Tools

### `chroma_sequential_thinking`

Records a thought in a sequential thinking process.

#### Parameters for chroma_sequential_thinking

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `thought` | string | Yes | The current thought content |
| `thought_number` | integer | Yes | Position in the thought sequence (1-based) |
| `total_thoughts` | integer | Yes | Total expected thoughts in the sequence |
| `session_id` | string | No | Session identifier (default: "" = new session) |
| `branch_from_thought` | integer | No | Thought number this branches from (default: 0 = no branch) |
| `branch_id` | string | No | Branch identifier (default: "") |
| `next_thought_needed` | boolean | No | Whether another thought is needed (default: false) |
| `custom_data` | string | No | Additional metadata as JSON string |

#### Returns from chroma_sequential_thinking

A JSON object containing thought information and context.

#### Example for chroma_sequential_thinking

```json
{
  "thought": "The similarity search should use cosine distance for text embeddings",
  "thought_number": 2,
  "total_thoughts": 5,
  "session_id": "problem-solving-123",
  "custom_data": {
    "domain": "vector_search",
    "confidence": 0.85
  }
}
```

### `chroma_find_similar_thoughts`

Finds similar thoughts across all or specific thinking sessions.

#### Parameters for chroma_find_similar_thoughts

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | The thought or concept to search for |
| `n_results` | integer | No | Number of similar thoughts to return (default: 5) |
| `threshold` | number | No | Similarity threshold (0.0-1.0, default: -1.0 = use 0.75) |
| `session_id` | string | No | Session ID to limit search scope (default: "" = global) |
| `include_branches` | boolean | No | Whether to include thoughts from branch paths (default: true) |

#### Returns from chroma_find_similar_thoughts

A JSON object containing similar thoughts and their metadata.

#### Example for chroma_find_similar_thoughts

```json
{
  "query": "vector database optimization techniques",
  "n_results": 3,
  "threshold": 0.8
}
```

### `chroma_get_session_summary`

Gets a summary of all thoughts in a thinking session.

#### Parameters for chroma_get_session_summary

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `session_id` | string | Yes | The session identifier |
| `include_branches` | boolean | No | Whether to include branching thought paths (default: true) |

#### Returns from chroma_get_session_summary

A JSON object containing session thoughts and metadata.

#### Example for chroma_get_session_summary

```json
{
  "session_id": "problem-solving-123",
  "include_branches": true
}
```

### `chroma_find_similar_sessions`

Finds thinking sessions with similar content or patterns.

#### Parameters for chroma_find_similar_sessions

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | The concept or pattern to search for |
| `n_results` | integer | No | Number of similar sessions to return (default: 5) |
| `threshold` | number | No | Similarity threshold (0.0-1.0, default: -1.0 = use 0.75) |

#### Returns from chroma_find_similar_sessions

A JSON object containing similar sessions and their summaries.

#### Example for chroma_find_similar_sessions

```json
{
  "query": "problem solving for vector search optimization",
  "n_results": 5,
  "threshold": 0.7
}
```

### `chroma_log_chat`

Log chat interaction with enhanced context for future retrieval and bidirectional linking with code.

#### Parameters for chroma_log_chat

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `prompt_summary` | string | Yes | Summary of the user's prompt/question |
| `response_summary` | string | Yes | Summary of the AI's response/solution |
| `raw_prompt` | string | No | Full text of the user's prompt |
| `raw_response` | string | No | Full text of the AI's response |
| `tool_usage` | array | No | List of tools used during the interaction |
| `file_changes` | array | No | List of files modified with before/after content |
| `involved_entities` | string | No | Comma-separated string of entities involved in the interaction (e.g., file paths, function names) |
| `session_id` | string | No | Session ID for the interaction (UUID). Generated if not provided |
| `collection_name` | string | No | Name of the ChromaDB collection to log to (default: "chat_history_v1") |
| `modification_type` | string | No | Type of change (refactor, bugfix, feature, etc.) |
| `confidence_score` | float | No | Confidence in the value of the interaction (0.0-1.0) |
| `code_context` | object | No | JSON object containing before/after code snippets of modified files |
| `diff_summary` | string | No | Concise description of the code changes made |
| `tool_sequence` | string | No | Sequence of tools used in the interaction (e.g., "read_file→edit_file") |
| `related_code_chunks` | array | No | References to chunk_ids from codebase_v1 that were modified |

#### Returns from chroma_log_chat

A JSON object containing:

- `success`: Boolean indicating whether the operation was successful
- `chat_id`: ID of the created chat document if successful
- `error`: Error message if unsuccessful
- `bidirectional_links`: Information about established connections between chat entry and code chunks

#### Bidirectional Linking

When code changes are included, the tool automatically:

1. Identifies the relevant code chunks that were modified
2. Updates the chat entry's `related_code_chunks` field with references to those chunks
3. Updates each code chunk's `related_chat_ids` metadata to include this chat ID
4. Creates a navigable history between discussions and code changes

This bidirectional linking enables powerful capabilities:

- Finding all discussions related to a specific code file or function
- Seeing all code affected by a particular discussion
- Tracing the evolution of a feature or fix across multiple conversations

#### Example for chroma_log_chat

```json
{
  "prompt_summary": "Update API documentation for log-chat command",
  "response_summary": "Added comprehensive documentation for log-chat in API reference",
  "raw_prompt": "Please update the documentation to include log-chat command...",
  "raw_response": "I've updated the API reference with detailed information...",
  "tool_usage": [
    {"name": "read_file", "args": {"path": "docs/api_reference.md"}},
    {"name": "edit_file", "args": {"path": "docs/api_reference.md"}}
  ],
  "file_changes": [
    {
      "file_path": "docs/api_reference.md",
      "before_content": "... original content ...",
      "after_content": "... modified content ..."
    }
  ],
  "involved_entities": "docs/api_reference.md,log-chat,documentation",
  "modification_type": "documentation",
  "confidence_score": 0.85,
  "tool_sequence": "read_file→edit_file"
}
```

---

## Error Handling

All tools follow a consistent error handling pattern. Errors will be returned with:

- An error code
- A descriptive message
- Additional details when available

Common error types:

| Error | Description |
|-------|-------------|
| `ValidationError` | Input validation failures |
| `CollectionNotFoundError` | Requested collection doesn't exist |
| `DocumentNotFoundError` | Requested document doesn't exist |
| `ChromaDBError` | Errors from the underlying ChromaDB |
| `McpError` | General MCP-related errors |

## Configuration

### Command-line Arguments

- `--cpu-execution-provider`: Force CPU execution provider for embedding functions (`auto`, `true`, `false`)
- `--default-ef`: Name of the default embedding function (e.g., `default`, `openai`)

### Environment Variables

Equivalent environment variables can be used (e.g., `CHROMA_CLIENT_TYPE`, `CHROMA_DATA_DIR`, `CHROMA_DEFAULT_EF`). Command-line arguments take precedence.

## Document Management Tools (`document_tools.py`)

Tools for adding, updating, retrieving, and deleting individual documents within a collection.

## Thinking Tools (`thinking_tools.py`)

These tools facilitate creating a persistent, searchable "working memory" for AI development workflows by managing sequences of thoughts within sessions.

See the [Embeddings and Thinking Tools Guide](thinking_tools/embeddings_and_thinking.md) for concepts and use cases.

### `mcp_chroma_test_chroma_sequential_thinking`

Records a single thought in a sequential chain within a session. If `session_id` is empty, a new session is created.

**Parameters:**

- `thought` (string, required): Content of the thought being recorded.
- `thought_number` (int, required): Sequential number of this thought within the session/branch (must be > 0).
- `total_thoughts` (int, required): Total anticipated number of thoughts in this sequence (used for context, may not be strictly enforced).
- `session_id` (string, optional): Unique ID for the thinking session. If empty, a new UUID is generated.
- `branch_id` (string, optional): Identifier for a specific branch within the session. Empty for the main trunk.
- `branch_from_thought` (int, optional, default: 0): If creating a new branch (`branch_id` is provided), specifies the parent `thought_number` (> 0) this branch originates from. 0 indicates not branching or starting a branch from the beginning.
- `next_thought_needed` (bool, optional, default: False): Flag indicating if a subsequent thought is expected in this sequence.

**Returns:**

JSON object with `session_id` and the generated `thought_id`.

**Example:**

```json
{
  "tool_name": "mcp_chroma_test_chroma_sequential_thinking",
  "arguments": {
    "session_id": "sess_123",
    "thought_number": 1,
    "total_thoughts": 3,
    "thought": "User asked to implement the login function."
  }
}
```

### `mcp_chroma_test_chroma_find_similar_thoughts`

Finds thoughts semantically similar to a given query text, potentially within a specific session.

**Parameters:**

- `query` (string, required): Text to search for similar thoughts.
- `session_id` (string, optional): If provided, limits the search to thoughts within this specific session.
- `n_results` (int, optional, default: 5): Maximum number of similar thoughts to return (must be >= 1).
- `threshold` (float, optional, default: -1.0): Similarity score threshold (0.0 to 1.0, lower distance is more similar). A value of -1.0 uses the server-defined default (currently 0.75). Similarity is calculated as `1.0 - distance`.
- `include_branches` (bool, optional, default: True): Whether to include thoughts from branches when searching within a session.

**Returns:**

JSON object containing a list of `similar_thoughts` (each with `id`, `content`, `metadata`, `similarity`), `total_found`, and `threshold_used`.

**Example:**

```json
{
  "tool_name": "mcp_chroma_test_chroma_find_similar_thoughts",
  "arguments": {
    "session_id": "sess_123",
    "query": "What was the plan for the login function?",
    "n_results": 3
  }
}
```

### `mcp_chroma_test_chroma_get_session_summary`

Retrieves all thoughts recorded within a specific thinking session, ordered sequentially.

**Parameters:**

- `session_id` (string, required): The unique identifier for the thinking session to summarize.
- `include_branches` (bool, optional, default: True): Whether to include thoughts from branches in the summary.

**Returns:**

JSON object containing `session_id`, a list of `session_thoughts` (each with `id`, `content`, `metadata`), and `total_thoughts_in_session`.

**Example:**

```json
{
  "tool_name": "mcp_chroma_test_chroma_get_session_summary",
  "arguments": {
    "session_id": "sess_123"
  }
}
```

### `mcp_chroma_test_chroma_find_similar_sessions`

Finds thinking sessions whose overall content is semantically similar to a query text. (Note: Requires session summaries to be pre-computed or aggregated).

**Parameters:**

- `query` (string, required): Text to search for similar thinking sessions.
- `n_results` (int, optional, default: 5): Maximum number of similar sessions to return (must be >= 1).
- `threshold` (float, optional, default: -1.0): Similarity score threshold (0.0 to 1.0, lower distance is more similar). A value of -1.0 uses the server-defined default (currently 0.75).

**Returns:**

JSON object containing a list of `similar_sessions` (each potentially including `session_id`, summary snippet, `similarity_score`), `total_found`, and `threshold_used`.

**Example:**

```json
{
  "tool_name": "mcp_chroma_test_chroma_find_similar_sessions",
  "arguments": {
    "query": "Find sessions discussing database schema changes",
    "n_results": 3
  }
}
```

## Other Tools

### Setup Collections Command

```bash
chroma-mcp-client setup-collections [-v]
```

Sets up all required collections for the Chroma MCP Server. This is useful for new installations or ensuring all collections exist.

Options:

- `-v`, `--verbose`: Increase verbosity (use multiple times for more detailed logs: -v, -vv)

#### Promote Learning Command

```bash
chroma-mcp-client promote-learning DESCRIPTION [--pattern PATTERN] [--code-ref CODE_REF] 
                              [--tags TAGS] [--confidence CONFIDENCE] 
                              [--source-chat-id ID] [--collection-name NAME] 
                              [--include-chat-context] [--require-validation]
                              [--validation-evidence-id ID] [--validation-score SCORE]
                              [--validation-threshold THRESHOLD]
```

Promotes a learning to the derived learnings collection.

Arguments:

- `DESCRIPTION`: Text description of the derived learning

Options:

- `--pattern`: Sample code pattern this learning applies to
- `--code-ref`: Reference to code that demonstrates the learning (format: "path:commit:line")
- `--tags`: Comma-separated tags for categorizing the learning
- `--confidence`: Confidence score between 0 and 1 (defaults to 0.5)
- `--source-chat-id`: Optional ID of source chat for context
- `--collection-name`: Name of the target collection (defaults to "derived_learnings_v1")
- `--chat-collection-name`: Name of the chat history collection (defaults to "chat_history_v1")
- `--include-chat-context`: Include full chat context when linking to source chat
- `--require-validation`: Require validation evidence for promotion
- `--validation-evidence-id`: ID of validation evidence to associate with the learning
- `--validation-score`: Manual validation score (0.0-1.0) if no evidence ID provided
- `--validation-threshold`: Minimum required validation score (defaults to 0.7)

#### Log Error Command

```bash
chroma-mcp-client log-error --error-type TYPE --error-message MSG
                       [--stacktrace TRACE] [--affected-files FILES]
                       [--resolution RES] [--resolution-verified]
                       [--collection-name NAME]
```

Logs a runtime error for validation evidence.

Required:

- `--error-type`: Type of the error (e.g., ValueError, TypeError)
- `--error-message`: Error message content

Options:

- `--stacktrace`: Full stacktrace of the error
- `--affected-files`: Comma-separated list of affected file paths
- `--resolution`: Description of how the error was resolved
- `--resolution-verified`: Flag indicating the resolution has been verified
- `--collection-name`: Name of the collection to store evidence (defaults to "validation_evidence_v1")

#### Log Test Results Command

```bash
chroma-mcp-client log-test-results XML_PATH [--before-xml PATH]
                              [--commit-before HASH] [--commit-after HASH]
                              [--collection-name NAME]
```

Logs test results from JUnit XML files for validation evidence.

Arguments:

- `XML_PATH`: Path to the JUnit XML test results file

Options:

- `--before-xml`: Path to a previous JUnit XML file for comparison
- `--commit-before`: Git commit hash for the "before" state
- `--commit-after`: Git commit hash for the "after" state
- `--collection-name`: Name of the collection to store evidence (defaults to "test_results_v1")

#### Log Quality Check Command

```bash
chroma-mcp-client log-quality-check --tool TOOL --after-output PATH
                              [--before-output PATH] [--metric-type TYPE]
                              [--collection-name NAME]
```

Logs code quality metrics for validation evidence.

Required:

- `--tool`: Quality tool name (e.g., "pylint", "ruff", "flake8")
- `--after-output`: Path to the output file of the tool after changes

Options:

- `--before-output`: Path to the output file of the tool before changes (for comparison)
- `--metric-type`: Type of metric (defaults to "error_count", options: "linting", "complexity", "coverage")
- `--collection-name`: Name of the collection to store evidence (defaults to "validation_evidence_v1")

#### Validate Evidence Command

```bash
chroma-mcp-client validate-evidence [--evidence-file PATH] [--test-transitions IDS]
                              [--runtime-errors IDS] [--code-quality IDS]
                              [--threshold NUM] [--output-file PATH]
```

Validates evidence for learning promotion.

At least one of these evidence sources must be provided:

- `--evidence-file`: Path to a JSON file containing validation evidence
- `--test-transitions`: Comma-separated list of test transition evidence IDs
- `--runtime-errors`: Comma-separated list of runtime error evidence IDs
- `--code-quality`: Comma-separated list of code quality evidence IDs

Options:

- `--threshold`: Validation score threshold for promotion eligibility (defaults to 0.7)
- `--output-file`: Path to save the validation results as JSON
