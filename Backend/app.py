import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import UPLOAD_DIR, VECTORSTORE_DIR
from ingest import ingest_pdf, load_vectorstore
from rag_chain import get_answer

app = FastAPI(title="RAG PDF Chatbot")

# Allow frontend (running on a different port/origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Make sure required folders exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# In-memory store: keeps the currently loaded vectorstore for this session
current_vectorstore = None


class QuestionRequest(BaseModel):
    question: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, save it, and build a vectorstore from its contents.
    """
    global current_vectorstore

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Save uploaded file to uploads/
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Build vectorstore from this PDF (collection name = filename without extension)
    import re
    raw_name = os.path.splitext(file.filename)[0]
    collection_name = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_name)
    collection_name = collection_name.strip("_-")
    if len(collection_name) < 3:
        collection_name = f"pdf_{collection_name}"
    collection_name = collection_name[:63]

    current_vectorstore = ingest_pdf(save_path, collection_name=collection_name)

    return {"message": f"'{file.filename}' uploaded and processed successfully."}


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Ask a question. Uses the currently loaded vectorstore (from /upload).
    Falls back to general knowledge if the question isn't covered by the PDF.
    """
    global current_vectorstore

    if current_vectorstore is None:
        raise HTTPException(
            status_code=400,
            detail="No PDF uploaded yet. Please upload a PDF first via /upload.",
        )

    answer = get_answer(request.question, current_vectorstore)
    return {"answer": answer}


@app.get("/")
async def root():
    return {"status": "RAG Chatbot backend is running."}