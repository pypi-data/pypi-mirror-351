# 🧠 NeuroCache

NeuroCache is a lightweight AI memory system for Python. It lets you store, search, and update memories using embeddings.

## Features

- Add/update/delete text memories with associated metadata (user_id, title, name, custom fields).
- Search memories using semantic (cosine) similarity.
- Filter searches by `user_id` or other custom metadata fields.
- Persistent storage using ChromaDB (default: `.chromadb_neurocache` folder).
- Uses Sentence Transformers for generating embeddings (default: `all-MiniLM-L6-v2`).
- Configurable logging for easier debugging.
- Retrieve memories by their unique ID.
- Count total memories.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from neurocache import NeuroCache
import logging

# Optional: Configure logging to see NeuroCache's operations
logging.basicConfig(level=logging.INFO)

# 1. Initialize NeuroCache
# This will create a .chromadb_neurocache directory in your project for persistence
neurocache = NeuroCache()

# You can also customize the model, collection name, and persistence directory:
# neurocache = NeuroCache(
#     model_name='paraphrase-MiniLM-L3-v2',  # Choose another SentenceTransformer model
#     collection_name='my_personal_memories',
#     persist_directory='./my_secret_db'
# )

# 2. Add a Memory
user_id = "user_123"
memory_text = "Today, I had a productive meeting about the upcoming product launch with Sarah and David."
memory_title = "Product Launch Sync"
memory_name = "Meeting_20250530_ProductLaunch"
custom_details = {"project_code": "X7", "attendees": ["Sarah", "David"]}

memory_id = neurocache.add(
    text_content=memory_text,
    user_id=user_id,
    title=memory_title,
    name=memory_name,
    metadata=custom_details
)

if memory_id:
    print(f"Memory added successfully! ID: {memory_id}")
else:
    print("Failed to add memory.")

# 3. Search for Memories
query = "meeting about product launch"
search_results = neurocache.search(query_text=query, n_results=3, user_id=user_id)

print(f"\nFound {len(search_results)} memories for query '{query}':")
for result in search_results:
    print(f"  ID: {result['id']}")
    print(f"  Text: {result['text_content']}")
    print(f"  Title: {result['metadata']['title']}")
    print(f"  User ID: {result['metadata']['user_id']}")
    print(f"  Distance: {result['distance']:.4f}")
    print(f"  Created At: {result['metadata']['created_at_utc']}")
    print(f"  Custom Metadata: { {k:v for k,v in result['metadata'].items() if k not in ['user_id', 'title', 'name', 'original_text', 'created_at_utc', 'updated_at_utc']} }") # Displaying only truly custom fields
    print("-" * 10)

# 4. Retrieve a specific memory
if memory_id:
    retrieved_mem = neurocache.get_by_id(memory_id)
    if retrieved_mem:
        print(f"\nRetrieved memory by ID ({memory_id}):")
        print(f"  Text: {retrieved_mem['text_content']}")
        print(f"  Metadata: {retrieved_mem['metadata']}")

# 5. Update a memory
if memory_id:
    update_success = neurocache.update(
        memory_id=memory_id,
        new_text_content="The product launch meeting also covered marketing budget.",
        new_custom_metadata={"budget_discussed": True} # Adds to existing metadata
    )
    if update_success:
        print(f"\nMemory {memory_id} updated.")
        updated_mem = neurocache.get_by_id(memory_id)
        if updated_mem:
             print(f"  New text: {updated_mem['text_content']}")
             print(f"  Updated metadata now includes: \'budget_discussed\': {updated_mem['metadata'].get('budget_discussed')}")


# 6. Delete a memory
if memory_id:
    delete_success = neurocache.delete(memory_id)
    if delete_success:
        print(f"\nMemory {memory_id} deleted.")
    else:
        print(f"\nFailed to delete memory {memory_id}.")

# 7. Count memories
total_memories = neurocache.count()
print(f"\nTotal memories currently stored: {total_memories}")

```

## Core Components

- **`NeuroCache` Class (`neurocache/memory.py`)**: The main interface for interacting with the memory system.

  - `__init__(model_name=None, collection_name=None, persist_directory=None)`: Initializes the system.
    - `model_name`: SentenceTransformer model (default: `all-MiniLM-L6-v2`).
    - `collection_name`: ChromaDB collection name (default: `neurocache_cache`).
    - `persist_directory`: Path for ChromaDB persistence (default: `.chromadb_neurocache`).
  - `add(text_content, user_id, title, name, metadata=None)`: Adds a memory.
    - `text_content` (str): The core text.
    - `user_id` (str): Identifier for the user.
    - `title` (str): General title for the memory.
    - `name` (str): More specific name/identifier.
    - `metadata` (dict, optional): Custom key-value pairs.
    - Returns the unique `memory_id` (str) or `None`.
  - `search(query_text, n_results=5, user_id=None, search_filter=None)`: Searches memories.
    - `query_text` (str): Text to search for.
    - `n_results` (int): Number of results to return.
    - `user_id` (str, optional): Filter by user.
    - `search_filter` (dict, optional): Filter by custom metadata (e.g., `{"category": "work"}`).
    - Returns a list of result dictionaries. Each result includes `id`, `text_content`, `metadata`, and `distance`.
  - `update(memory_id, new_text_content=None, new_user_id=None, new_title=None, new_name=None, new_custom_metadata=None)`: Updates an existing memory.
    - Provide `memory_id` and any fields to change. If `new_text_content` is given, its embedding is re-calculated.
    - Returns `True` on success, `False` otherwise.
  - `delete(memory_id)`: Deletes a memory by its ID.
    - Returns `True` on success, `False` otherwise.
  - `get_by_id(memory_id)`: Retrieves a memory by its ID.
    - Returns a dictionary with `id`, `text_content`, `metadata` or `None`.
  - `count()`: Returns the total number of memories.

- **`EmbeddingGenerator` Class (`neurocache/embeddings.py`)**: Handles the creation of text embeddings using Sentence Transformers.

  - `generate(text)`: Takes a string and returns its embedding as a list of floats.

- **`ChromaStorage` Class (`neurocache/storage.py`)**: Manages the interaction with the ChromaDB vector store.

  - Handles adding, querying, updating, and deleting embedding vectors and their associated metadata.
  - Metadata stored includes: `user_id`, `title`, `name`, `original_text`, `created_at_utc`, `updated_at_utc`, and any custom metadata provided.

- **Configuration (`neurocache/config.py`)**:
  - `DEFAULT_MODEL_NAME`: Default SentenceTransformer model.
  - `CHROMA_PERSIST_DIRECTORY`: Default directory for ChromaDB data.
  - `DEFAULT_COLLECTION_NAME`: Default ChromaDB collection name.
  - Basic logging setup.

## Debugging

NeuroCache uses Python's `logging` module. To see detailed logs of its operations:

```python
import logging
logging.basicConfig(level=logging.INFO) # Or logging.DEBUG for more verbosity

# Then use NeuroCache as usual
from neurocache import NeuroCache
neurocache = NeuroCache()
# ... your operations ...
```

This will output information about model loading, database interactions, additions, searches, etc., to your console.

## Running the Example

An example script is provided in `examples/basic_usage.py`. To run it:

1.  Make sure you have installed the package in editable mode:
    ```bash
    pip install -e .
    ```
2.  Navigate to the root directory of the `neurocache` project.
3.  Run the example:
    ```bash
    python examples/basic_usage.py
    ```

This will demonstrate adding, searching, updating, and deleting memories, printing logs to your console. A `.chromadb_neurocache` directory will be created in your project root to store the database.
