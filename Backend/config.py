import os
from dotenv import load_dotenv

load_dotenv()

# Groq API key (set this in a .env file as GROQ_API_KEY=gsk_...)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # HuggingFace embedding model
CHAT_MODEL = "openai/gpt-oss-20b"  # ChatGroq model

# Chunking settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Paths
UPLOAD_DIR = "uploads"
VECTORSTORE_DIR = "vectorstore"

# Retrieval settings
TOP_K = 4
# Similarity score threshold (0-1, lower distance = more similar in Chroma).
# Used to decide whether retrieved context is "relevant enough" to use,
# vs falling back to the LLM's general knowledge.
RELEVANCE_SCORE_THRESHOLD = 1.8