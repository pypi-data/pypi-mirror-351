import logging

# Configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for SentenceTransformer model
DEFAULT_MODEL_NAME = 'all-MiniLM-L6-v2'

# Configuration for ChromaDB
# In-memory client:
# CHROMA_CLIENT_SETTINGS = {} 
# Persistent client:
# CHROMA_CLIENT_SETTINGS = {"persist_directory": ".chromadb"} # Creates a .chromadb folder in your project
CHROMA_PERSIST_DIRECTORY = ".chromadb_neurocache"
DEFAULT_COLLECTION_NAME = "neurocache_cache"
