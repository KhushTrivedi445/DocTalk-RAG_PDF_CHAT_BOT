📖 DocTalk — Smart PDF Chat Bot

DocTalk is a RAG-based (Retrieval-Augmented Generation) chatbot that lets you upload any PDF and have a natural conversation about it. Unlike a strict "PDF-only" chatbot, DocTalk is hybrid: if your question is answered within the document, it grounds its response in that content — but if you ask something outside the PDF (e.g. follow-up general knowledge questions), it seamlessly falls back to its own knowledge to keep the conversation flowing.

The PDF is rendered page-by-page right next to the chat, so you can read along while you ask questions.


✨ Features


📄 Upload & Analyze — upload any PDF, which gets chunked, embedded, and indexed into a vector store.
💬 Hybrid Chat — answers grounded in your PDF when relevant, with graceful fallback to general knowledge for unrelated questions.
🖼️ Read Alongside — PDF pages are rendered as images directly in the UI alongside the chat.
⚡ Live "Thinking..." indicator — see your message instantly and watch the bot think before it responds.
🎨 Custom dark-themed UI built with Streamlit.



🛠️ Tech Stack

Backend


FastAPI — REST API server
LangChain — RAG orchestration
ChromaDB — vector store for embeddings
HuggingFace Embeddings (sentence-transformers/all-MiniLM-L6-v2) — local embedding model
Groq (langchain-groq) — LLM inference via openai/gpt-oss-20b
PyPDF — PDF text extraction


Frontend


Streamlit — interactive web UI
PyMuPDF (fitz) — render PDF pages as images
Pillow — image handling
Requests — communication with backend API



📁 Project Structure

RAG-PDF-CHAT-BOT/
├── backend/
│   ├── app.py             # FastAPI server (upload + ask endpoints)
│   ├── ingest.py           # PDF loading, chunking, embedding, vectorstore
│   ├── rag_chain.py         # Hybrid retrieval + LLM answer logic
│   ├── config.py            # Central configuration (models, paths, thresholds)
│   ├── .env                 # API keys (not committed)
│   ├── uploads/              # Uploaded PDFs (auto-created)
│   └── vectorstore/           # Persisted Chroma vector DBs (auto-created)
│
├── frontend/
│   └── streamlit_app.py     # Streamlit UI
│
├── requirements.txt          # Python dependencies
└── README.md


⚙️ Setup & Installation

1. Clone the repository

bashgit clone https://github.com/<your-username>/RAG-PDF-CHAT-BOT.git
cd RAG-PDF-CHAT-BOT

2. Create and activate a virtual environment

bashpython -m venv myenv

# Windows
myenv\Scripts\activate

# macOS / Linux
source myenv/bin/activate

3. Install dependencies

bashpip install -r requirements.txt

4. Configure environment variables

Create a .env file inside the backend/ folder:

GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here


Get a free Groq API key at console.groq.com.

The HuggingFace token isn't strictly required since embeddings run locally, but is good to have set.




▶️ Running the App

You need two terminals running simultaneously — one for the backend, one for the frontend.

Terminal 1 — Start the backend (FastAPI)

bashcd backend
uvicorn app:app --reload

The backend will run at: http://127.0.0.1:8000

You can view the interactive API docs at: http://127.0.0.1:8000/docs

Terminal 2 — Start the frontend (Streamlit)

bashcd frontend
streamlit run streamlit_app.py

The app will open in your browser at: http://localhost:8501


🚀 How to Use


Open the Streamlit app in your browser.
In the sidebar, upload a PDF file.
Click 🔎 Start Analyse — this sends the PDF to the backend, where it's chunked, embedded, and indexed.
Once analysis is complete, the PDF will render on the left and the chat will appear on the right.
Ask any question:

Questions about the PDF content → answered using retrieved context from the document.
Questions outside the PDF → answered using the model's general knowledge.



Use 🗑️ Clear chat in the sidebar to reset the conversation (without re-uploading the PDF).



🔧 Configuration

All key settings live in backend/config.py:

SettingDescriptionDefaultEMBEDDING_MODELHuggingFace embedding modelsentence-transformers/all-MiniLM-L6-v2CHAT_MODELGroq LLM modelopenai/gpt-oss-20bCHUNK_SIZEText chunk size for splitting PDF1000CHUNK_OVERLAPOverlap between chunks200TOP_KNumber of chunks retrieved per query4RELEVANCE_SCORE_THRESHOLDMax L2 distance for a chunk to be considered relevant1.8


🧩 How It Works (RAG Pipeline)


Ingestion (ingest.py): PDF → text → split into overlapping chunks → embedded via HuggingFace model → stored in a Chroma vector database (persisted to disk per-document).
Retrieval (rag_chain.py): On each question, the vectorstore is searched for the most similar chunks via similarity search with distance scoring.
Hybrid Decision:

If relevant chunks are found (distance ≤ threshold) → context is passed to the LLM along with the question (RAG prompt).
If no relevant chunks are found → the question is answered purely from the LLM's general knowledge (general prompt).



Generation: The Groq-hosted LLM (openai/gpt-oss-20b) generates the final response.



📦 Requirements

fastapi
uvicorn[standard]
python-multipart
pypdf
langchain
langchain-community
langchain-groq
langchain-huggingface
sentence-transformers
chromadb
tiktoken
python-dotenv
streamlit
PyMuPDF
pillow
requests


📝 Notes


The vectorstore is persisted per-PDF (based on a sanitized filename), so re-uploading the same PDF won't require re-indexing if the vectorstore already exists on disk.
RELEVANCE_SCORE_THRESHOLD may need tuning depending on the embedding model and document type — lower distance = more similar.
Ensure the backend (http://127.0.0.1:8000) is running before starting the frontend, otherwise API calls will fail with a connection error.



📄 License

This project is open-source and available under the MIT License.
