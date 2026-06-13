import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import (
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    UPLOAD_DIR,
    VECTORSTORE_DIR,
)


def get_embeddings():
    """Return the HuggingFace embedding model (runs locally)."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def ingest_pdf(pdf_path: str, collection_name: str = "pdf_collection"):
    """
    Load a PDF, split it into chunks, embed the chunks, and store
    them in a Chroma vectorstore persisted on disk.

    Returns the Chroma vectorstore object.
    """
    # 1. Load the PDF (each page becomes a Document with text + metadata)
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # 2. Split documents into smaller overlapping chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    # 3. Create embeddings model
    embeddings = get_embeddings()

    # 4. Store chunks + embeddings in Chroma (persisted to disk)
    persist_path = os.path.join(VECTORSTORE_DIR, collection_name)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_path,
    )

    return vectorstore


def load_vectorstore(collection_name: str = "pdf_collection"):
    """Load an existing persisted vectorstore from disk."""
    embeddings = get_embeddings()
    persist_path = os.path.join(VECTORSTORE_DIR, collection_name)
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_path,
    )