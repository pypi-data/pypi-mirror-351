from .memory import NeuroCache
from .config import logger

__version__ = "0.1.0"

# You can also expose other classes if they are meant to be used directly by the user
# from .storage import ChromaStorage
# from .embeddings import EmbeddingGenerator

logger.info(f"Memora package initialized (version {__version__})")
