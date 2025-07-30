\
from .embeddings import EmbeddingGenerator
from .storage import ChromaStorage
from .config import logger
from datetime import datetime

class NeuroCache:
    def __init__(self, model_name=None, collection_name=None, persist_directory=None):
        """
        Initializes the NeuroCache system.

        Args:
            model_name (str, optional): The name of the SentenceTransformer model to use. 
                                       Defaults to 'all-MiniLM-L6-v2'.
            collection_name (str, optional): The name of the ChromaDB collection. 
                                            Defaults to 'neurocache_cache'.
            persist_directory (str, optional): The directory to persist ChromaDB data. 
                                               Defaults to '.chromadb_neurocache'.
        """
        try:
            self.embed_generator = EmbeddingGenerator(model_name=model_name) if model_name else EmbeddingGenerator()
            
            storage_kwargs = {}
            if collection_name:
                storage_kwargs['collection_name'] = collection_name
            if persist_directory:
                storage_kwargs['persist_directory'] = persist_directory
            self.storage = ChromaStorage(**storage_kwargs)
            
            logger.info("NeuroCache system initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing NeuroCache system: {e}")
            raise

    def add(self, text_content, user_id, title, name, metadata=None):
        """
        Adds a new memory.

        Args:
            text_content (str): The textual content of the memory.
            user_id (str): The ID of the user associated with this memory.
            title (str): A title for the memory.
            name (str): A name or identifier for the memory (can be more specific than title).
            metadata (dict, optional): Additional custom metadata to store with the memory.

        Returns:
            str: The ID of the newly added memory, or None if an error occurred.
        """
        if not all([text_content, user_id, title, name]):
            logger.error("Missing required fields for adding memory (text_content, user_id, title, name).")
            return None
        try:
            embedding = self.embed_generator.generate(text_content)
            if embedding is None:
                logger.error(f"Failed to generate embedding for text: {text_content[:50]}...")
                return None
            
            memory_id = self.storage.add_memory(
                embedding=embedding,
                text_content=text_content,
                user_id=user_id,
                title=title,
                name=name,
                metadata=metadata
            )
            return memory_id
        except Exception as e:
            logger.error(f"Error in NeuroCache add operation: {e}")
            return None

    def search(self, query_text, n_results=5, user_id=None, search_filter=None):
        """
        Searches for memories similar to the query text.

        Args:
            query_text (str): The text to search for.
            n_results (int, optional): The maximum number of results to return. Defaults to 5.
            user_id (str, optional): Filter results by user ID. Defaults to None (search all users).
            search_filter (dict, optional): Additional key-value filters for metadata. 
                                          Example: {"category": "work"}
                                          Note: user_id filter is handled separately for clarity.

        Returns:
            list: A list of search result dictionaries, or an empty list if no results or an error.
                  Each dictionary contains 'id', 'text_content', 'metadata', and 'distance'.
        """
        if not query_text:
            logger.error("Search query text cannot be empty.")
            return []
        try:
            query_embedding = self.embed_generator.generate(query_text)
            if query_embedding is None:
                logger.error(f"Failed to generate embedding for query: {query_text[:50]}...")
                return []
            
            return self.storage.search_memories(
                query_embedding=query_embedding,
                n_results=n_results,
                user_id=user_id,
                search_filter=search_filter
            )
        except Exception as e:
            logger.error(f"Error in NeuroCache search operation: {e}")
            return []

    def update(self, memory_id, new_text_content=None, new_user_id=None, new_title=None, new_name=None, new_custom_metadata=None):
        """
        Updates an existing memory. 
        If new_text_content is provided, its embedding will be regenerated and updated.

        Args:
            memory_id (str): The ID of the memory to update.
            new_text_content (str, optional): New text content for the memory.
            new_user_id (str, optional): New user ID.
            new_title (str, optional): New title.
            new_name (str, optional): New name.
            new_custom_metadata (dict, optional): New or updated custom metadata fields. 
                                                 This will be merged with existing custom metadata.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if not memory_id:
            logger.error("Memory ID is required for update.")
            return False
            
        new_embedding = None
        if new_text_content:
            new_embedding = self.embed_generator.generate(new_text_content)
            if new_embedding is None:
                logger.error(f"Failed to generate new embedding for update (memory_id: {memory_id}). Update aborted for text content.")
                # Decide if you want to proceed with other metadata updates or abort all
                # For now, we abort if text is to be updated but embedding fails.
                return False

        metadata_updates = {}
        if new_user_id:
            metadata_updates["user_id"] = str(new_user_id)
        if new_title:
            metadata_updates["title"] = str(new_title)
        if new_name:
            metadata_updates["name"] = str(new_name)
        if new_custom_metadata: # merge new custom fields
             # To properly update nested custom metadata, one might need a deep merge.
             # For simplicity, this will overwrite top-level keys in custom_metadata if they exist.
             # Or, if you store all custom fields directly in the main metadata:
            metadata_updates.update(new_custom_metadata)


        try:
            return self.storage.update_memory(
                memory_id=memory_id,
                new_embedding=new_embedding, # Pass None if text not changing, or if embedding failed (already handled)
                new_text_content=new_text_content, # Pass None if text not changing
                new_metadata_fields=metadata_updates if metadata_updates else None
            )
        except Exception as e:
            logger.error(f"Error in NeuroCache update operation (memory_id: {memory_id}): {e}")
            return False

    def delete(self, memory_id):
        """
        Deletes a memory.

        Args:
            memory_id (str): The ID of the memory to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not memory_id:
            logger.error("Memory ID is required for delete.")
            return False
        try:
            return self.storage.delete_memory(memory_id)
        except Exception as e:
            logger.error(f"Error in NeuroCache delete operation (memory_id: {memory_id}): {e}")
            return False
            
    def get_by_id(self, memory_id):
        """
        Retrieves a specific memory by its ID.

        Args:
            memory_id (str): The ID of the memory to retrieve.

        Returns:
            dict: The memory data (id, text_content, metadata) or None if not found or error.
        """
        if not memory_id:
            logger.error("Memory ID is required for get_by_id.")
            return None
        try:
            return self.storage.get_memory_by_id(memory_id)
        except Exception as e:
            logger.error(f"Error in NeuroCache get_by_id operation (memory_id: {memory_id}): {e}")
            return None

    def count(self):
        """
        Counts the total number of memories.

        Returns:
            int: The total number of memories.
        """
        try:
            return self.storage.count_memories()
        except Exception as e:
            logger.error(f"Error in NeuroCache count operation: {e}")
            return 0
