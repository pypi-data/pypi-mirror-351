# Ragger Simple

A simple Python package for vector database operations using Qdrant, designed for semantic search and document retrieval.

## Features

- Initialize connection with Qdrant vector database (local or cloud)
- Parse, chunk, and process text into vector embeddings
- Search for relevant text chunks based on semantic similarity
- List collections in the database
- Purge collection data
- View collection statistics

## Use Cases

- Create a semantic search engine for your documents
- Build a question-answering system with context retrieval
- Implement similarity search for content recommendations
- Create a knowledge base with semantic retrieval

## Installation

```bash
pip install ragger-simple
```

## Usage

### Python API

Import and initialize `VectorDB`:

```python
from ragger_simple import VectorDB

db = VectorDB(
    collection_name="my_documents",
    model_name="all-MiniLM-L6-v2",
    model_path=None,
    qdrant_url=None,
    qdrant_api_key=None,
    qdrant_path=None,
    qdrant_timeout=500.0,
)
```

Constructor parameters:

- `collection_name` (str, default: `"documents"`) — Qdrant collection name  
- `model_name` (str, default: `"all-MiniLM-L6-v2"`) — sentence-transformers model  
- `model_path` (str, optional) — local folder with your model  
- `qdrant_url` (str, optional) — cloud URL (use with API key)  
- `qdrant_api_key` (str, optional) — cloud API key  
- `qdrant_path` (str, optional) — local path for database storage  
- `qdrant_timeout` (float, default: `500`) — request timeout in seconds

Methods:

```python
# Add documents to the database
db.add_documents(
    documents: Dict[str, str],
    chunk_size: int = 200,
    overlap: int = 50,
)

# Search for relevant chunks
results = db.search(
    query: str,
    k: int = 5,
) -> List[Dict]

# List all collections
collections = db.list_collections() -> List[str]

# Delete a collection
success = db.delete_collection(collection_name: Optional[str] = None) -> bool

# Purge all points from a collection but keep its structure
success = db.purge_collection(collection_name: Optional[str] = None) -> bool

# Get statistics about a collection
stats = db.get_collection_stats(collection_name: Optional[str] = None) -> Dict[str, Any]
```

Example:

```python
documents = {
    "Article 1": "This is the content of article 1...",
    "Article 2": "This is the content of article 2..."
}
db.add_documents(documents, chunk_size=200, overlap=50)
results = db.search("your query here", k=5)
print(results)
```

### CLI Commands

The CLI provides these commands:

```bash
# Initialize vector database (saves config for future commands)
ragger-simple init --model all-MiniLM-L6-v2 --collection documents --qdrant-url "https://your-qdrant-instance.com" --qdrant-key "your-api-key" --qdrant-path "/path/to/local/db"

# Process documents into vector database
ragger-simple process --input documents.json --chunk-size 200 --overlap 50

# Search for relevant chunks
ragger-simple search --query "your query here" --k 5 --output results.json

# List all collections
ragger-simple list-collections

# Delete all points from a collection but keep its structure
ragger-simple purge-collection --collection documents --confirm

# Completely delete a collection from the database
ragger-simple delete-collection --collection documents --confirm

# View collection statistics
ragger-simple collection-stats --collection documents
```

The CLI saves your connection settings in `~/.ragger-simple/config.json` for convenience.

## Configuration Guidelines

- **Collection naming**: Use descriptive names for different document sets
- **Chunk size**: 
  - Smaller (100-200 words): Better for precise Q&A
  - Larger (300-500 words): Better for contextual understanding
- **Model selection**:
  - `all-MiniLM-L6-v2`: Good balance of performance and speed
  - `all-mpnet-base-v2`: Higher quality but slower
- **Local vs Cloud**:
  - Local: Specify `qdrant_path` for persistence
  - Cloud: Use both `qdrant_url` and `qdrant_api_key`

## License

MIT
