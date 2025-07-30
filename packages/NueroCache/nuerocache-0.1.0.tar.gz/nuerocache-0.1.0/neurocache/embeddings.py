\
from sentence_transformers import SentenceTransformer
from .config import DEFAULT_MODEL_NAME, logger

class EmbeddingGenerator:
    def __init__(self, model_name=DEFAULT_MODEL_NAME):
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded SentenceTransformer model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading SentenceTransformer model {model_name}: {e}")
            raise

    def generate(self, text):
        if not text or not isinstance(text, str):
            logger.warning("Embedding generation called with empty or invalid text.")
            return None
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()  # Convert numpy array to list for ChromaDB
        except Exception as e:
            logger.error(f"Error generating embedding for text '{text[:50]}...': {e}")
            return None
