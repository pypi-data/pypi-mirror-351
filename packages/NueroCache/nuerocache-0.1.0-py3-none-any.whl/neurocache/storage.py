import chromadb
from .config import CHROMA_PERSIST_DIRECTORY, DEFAULT_COLLECTION_NAME, logger
import uuid
from datetime import datetime

class ChromaStorage:
    def __init__(self, collection_name=DEFAULT_COLLECTION_NAME, persist_directory=CHROMA_PERSIST_DIRECTORY):
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            # self.client = chromadb.Client() # For in-memory
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logger.info(f"ChromaDB client initialized. Collection '{collection_name}' loaded/created. Persisting to: {persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client or collection '{collection_name}': {e}")
            raise

    def add_memory(self, embedding, text_content, user_id, title, name, metadata=None):
        memory_id = str(uuid.uuid4())
        now_utc = datetime.utcnow()
        
        full_metadata = {
            "user_id": str(user_id),
            "title": str(title),
            "name": str(name),
            "original_text": str(text_content),
            "created_at_utc": now_utc.isoformat(),
            "updated_at_utc": now_utc.isoformat(),
            **(metadata or {})
        }

        if embedding is None:
            logger.error(f"Attempted to add memory with None embedding for text: {text_content[:50]}...")
            return None

        try:
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                metadatas=[full_metadata],
                documents=[text_content] # Storing the text directly in documents for easier retrieval if needed
            )
            logger.info(f"Memory added with ID: {memory_id}, UserID: {user_id}, Title: {title}")
            return memory_id
        except Exception as e:
            logger.error(f"Error adding memory to ChromaDB (ID: {memory_id}, UserID: {user_id}): {e}")
            return None

    def search_memories(self, query_embedding, n_results=5, user_id=None, search_filter=None):
        if query_embedding is None:
            logger.warning("Search called with None query embedding.")
            return []
        
        where_clause = {}
        if user_id:
            where_clause["user_id"] = str(user_id)
        if search_filter:
            where_clause.update(search_filter)
        
        # Ensure where_clause is None if empty, as ChromaDB expects None for no filter, not {}
        final_where_clause = where_clause if where_clause else None

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=final_where_clause,
                include=['metadatas', 'documents', 'distances']
            )
            logger.info(f"Search completed. Found {len(results.get('ids', [[]])[0])} results for UserID: {user_id if user_id else 'any'}.")
            
            # Restructure results for easier use
            output_results = []
            if results and results.get('ids') and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    res_item = {
                        "id": results['ids'][0][i],
                        "text_content": results['documents'][0][i] if results.get('documents') and results['documents'][0] else None,
                        "metadata": results['metadatas'][0][i] if results.get('metadatas') and results['metadatas'][0] else None,
                        "distance": results['distances'][0][i] if results.get('distances') and results['distances'][0] else None,
                    }
                    output_results.append(res_item)
            return output_results
        except Exception as e:
            logger.error(f"Error searching memories in ChromaDB (UserID: {user_id if user_id else 'any'}): {e}")
            return []

    def update_memory(self, memory_id, new_embedding=None, new_text_content=None, new_metadata_fields=None):
        try:
            # Fetch existing to preserve fields not being updated
            existing_memory = self.collection.get(ids=[memory_id], include=['metadatas', 'documents', 'embeddings'])
            if not existing_memory or not existing_memory['ids']:
                logger.warning(f"Memory with ID {memory_id} not found for update.")
                return False

            current_doc = existing_memory['documents'][0]
            current_meta = existing_memory['metadatas'][0]
            current_embedding = existing_memory['embeddings'][0]

            doc_to_update = new_text_content if new_text_content is not None else current_doc
            meta_to_update = current_meta.copy()
            if new_metadata_fields:
                meta_to_update.update(new_metadata_fields)
            meta_to_update["updated_at_utc"] = datetime.utcnow().isoformat()
            
            embedding_to_update = new_embedding if new_embedding is not None else current_embedding
            if new_text_content and new_embedding is None: # If text changes, embedding should ideally be re-generated
                logger.warning(f"Updating text for memory ID {memory_id} but not its embedding. Consider re-generating embedding.")


            self.collection.update(
                ids=[memory_id],
                embeddings=[embedding_to_update],
                metadatas=[meta_to_update],
                documents=[doc_to_update]
            )
            logger.info(f"Memory updated for ID: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating memory ID {memory_id} in ChromaDB: {e}")
            return False

    def delete_memory(self, memory_id):
        try:
            self.collection.delete(ids=[memory_id])
            logger.info(f"Memory deleted with ID: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory ID {memory_id} from ChromaDB: {e}")
            return False
            
    def get_memory_by_id(self, memory_id):
        try:
            result = self.collection.get(ids=[memory_id], include=['metadatas', 'documents'])
            if result and result['ids']:
                return {
                    "id": result['ids'][0],
                    "text_content": result['documents'][0] if result.get('documents') else None,
                    "metadata": result['metadatas'][0] if result.get('metadatas') else None,
                }
            logger.warning(f"Memory with ID {memory_id} not found.")
            return None
        except Exception as e:
            logger.error(f"Error retrieving memory ID {memory_id} from ChromaDB: {e}")
            return None

    def count_memories(self):
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting memories in ChromaDB: {e}")
            return 0
