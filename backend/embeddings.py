from sentence_transformers import SentenceTransformer

# Loaded once at startup, reused for every request
_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """Return a 384-dim embedding for a single string."""
    return _model.encode(text, normalize_embeddings=True).tolist()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.
    chunk_size: characters per chunk
    overlap: characters shared between consecutive chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]
