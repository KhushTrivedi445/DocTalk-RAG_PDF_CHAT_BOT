import streamlit as st
import requests
import fitz  # PyMuPDF
from PIL import Image
import io

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="DocTalk — PDF Chat", page_icon="📖", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0F1419; color: #E6E8EB; }

    section[data-testid="stSidebar"] { background-color: #161B22; }
    section[data-testid="stSidebar"] * { color: #E6E8EB !important; }
    section[data-testid="stSidebar"] .stButton button {
        background-color: #5B8DEF; color: #0F1419 !important;
        border: none; border-radius: 6px; font-weight: 700; width: 100%;
    }
    section[data-testid="stSidebar"] .stButton button:hover { background-color: #7BA3F5; }

    .stMarkdown, .stMarkdown p, .stMarkdown li, h1, h2, h3 { color: #E6E8EB; }

    .doctalk-mega-hero { text-align: center; padding: 3rem 1rem 1rem 1rem; }
    .doctalk-mega-hero h1 {
        font-family: 'Spectral', serif; font-weight: 800; font-size: 3rem;
        background: linear-gradient(135deg, #5B8DEF 0%, #9D7BF5 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 0.5rem; line-height: 1.2;
    }
    .doctalk-mega-hero p {
        font-family: 'JetBrains Mono', monospace; font-size: 0.95rem;
        color: #8B96A5; letter-spacing: 0.05em;
    }

    .doctalk-hero {
        display: flex; align-items: baseline; gap: 0.6rem;
        border-bottom: 3px solid #2A3340; padding-bottom: 0.5rem; margin-bottom: 1rem;
    }
    .doctalk-hero h1 { font-family: 'Spectral', serif; font-weight: 700; font-size: 2rem; color: #E6E8EB; margin: 0; }
    .doctalk-hero span {
        font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #5B8DEF;
        background: #1B2433; padding: 0.15rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em;
    }

    .pdf-page-wrapper {
        background: #1B2129; border: 1px solid #2A3340;
        margin-bottom: 1rem; padding: 6px; border-radius: 4px;
    }
    .pdf-page-label {
        font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #5C6878;
        text-align: center; margin-top: -0.5rem; margin-bottom: 0.8rem; letter-spacing: 0.1em;
    }

    .chat-panel-title {
        font-family: 'Spectral', serif; font-weight: 600; font-size: 1.3rem; color: #E6E8EB;
        border-bottom: 2px solid #2A3340; padding-bottom: 0.4rem; margin-bottom: 0.8rem;
    }

    .stChatMessage {
        border-radius: 10px; background-color: #1B2129 !important; border: 1px solid #2A3340;
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage span,
    .stChatMessage strong, .stChatMessage td, .stChatMessage th { color: #E6E8EB !important; }
    .stChatMessage table { background-color: #1B2129 !important; }

    .empty-state {
        border: 2px dashed #2A3340; border-radius: 10px; padding: 3rem 1.5rem;
        text-align: center; color: #8B96A5; font-family: 'Spectral', serif;
        font-size: 1.1rem; background: #161B22;
    }

    .feature-card {
        background: #161B22; border: 1px solid #2A3340; border-radius: 12px;
        padding: 1.6rem 1.2rem; text-align: center; height: 100%;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .feature-card:hover {
        border-color: #5B8DEF; transform: translateY(-3px);
    }
    .feature-card .feature-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .feature-card h4 {
        font-family: 'Spectral', serif; font-size: 1.05rem; color: #E6E8EB; margin: 0.3rem 0;
    }
    .feature-card p { font-size: 0.85rem; color: #8B96A5; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
defaults = {
    "messages": [],
    "pdf_uploaded": False,
    "pdf_analyzed": False,
    "pdf_name": None,
    "pdf_bytes": None,
    "pdf_pages": [],
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📖 DocTalk")
    st.markdown(
        "<span style='font-family:JetBrains Mono, monospace; font-size:0.75rem; opacity:0.7;'>"
        "ask anything · grounded in your pdf · or not</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**Upload a PDF**")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None and uploaded_file.name != st.session_state.pdf_name:
        st.session_state.pdf_bytes = uploaded_file.getvalue()
        st.session_state.pdf_name = uploaded_file.name
        st.session_state.pdf_uploaded = True
        st.session_state.pdf_analyzed = False
        st.session_state.messages = []

    if st.session_state.pdf_uploaded:
        st.markdown(f"**File:** `{st.session_state.pdf_name}`")

        if not st.session_state.pdf_analyzed:
            if st.button("🔎 Start Analyse"):
                with st.spinner("Analysing document — chunking, embedding, indexing..."):
                    files = {"file": (st.session_state.pdf_name, st.session_state.pdf_bytes, "application/pdf")}
                    try:
                        resp = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=300)
                        if resp.status_code == 200:
                            st.session_state.pdf_analyzed = True

                            doc = fitz.open(stream=st.session_state.pdf_bytes, filetype="pdf")
                            pages = []
                            for page in doc:
                                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                                img = Image.open(io.BytesIO(pix.tobytes("png")))
                                pages.append(img)
                            st.session_state.pdf_pages = pages
                            st.success("Document analysed and ready.")
                        else:
                            st.error(f"Analysis failed: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Can't reach backend. Is it running on port 8000?")
        else:
            st.success("✅ Document analysed")
            st.markdown(f"**Pages:** {len(st.session_state.pdf_pages)}")
            st.markdown("---")
            if st.button("🗑️ Clear chat"):
                st.session_state.messages = []
                st.rerun()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if not st.session_state.pdf_uploaded:
    st.markdown(
        """
        <div class="doctalk-mega-hero">
            <h1>YOUR SMART PDF CHAT BOT</h1>
            <p>UPLOAD · ANALYSE · CHAT</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="empty-state">
        👈 Upload a PDF from the sidebar to get started.<br>
        Then click <b>Start Analyse</b> to begin chatting.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <h4>Read Alongside</h4>
                <p>Your PDF renders right next to the chat so you never lose context.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h4>Grounded Answers</h4>
                <p>Questions are answered using the actual content of your document.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🌐</div>
                <h4>Beyond the PDF</h4>
                <p>Ask follow-ups outside the document — the bot still has your back.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
elif not st.session_state.pdf_analyzed:
    st.markdown(
        """
        <div class="doctalk-mega-hero">
            <h1>YOUR SMART PDF CHAT BOT</h1>
            <p>UPLOAD · ANALYSE · CHAT</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="empty-state">
        Document loaded — click <b>🔎 Start Analyse</b> in the sidebar
        to process it before chatting.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="doctalk-hero">
            <h1>DocTalk</h1>
            <span>PDF + GENERAL KNOWLEDGE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_pdf, col_chat = st.columns([1, 1], gap="large")

    with col_pdf:
        st.markdown('<div class="chat-panel-title">📄 Document</div>', unsafe_allow_html=True)
        pdf_container = st.container(height=650)
        with pdf_container:
            for i, page_img in enumerate(st.session_state.pdf_pages, start=1):
                st.markdown('<div class="pdf-page-wrapper">', unsafe_allow_html=True)
                st.image(page_img, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="pdf-page-label">PAGE {i} / {len(st.session_state.pdf_pages)}</div>',
                    unsafe_allow_html=True,
                )

    with col_chat:
        st.markdown('<div class="chat-panel-title">💬 Chat</div>', unsafe_allow_html=True)
        chat_container = st.container(height=580)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        prompt = st.chat_input("Ask about this PDF — or anything else...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            resp = requests.post(f"{BACKEND_URL}/ask", json={"question": prompt}, timeout=120)
                            if resp.status_code == 200:
                                answer = resp.json()["answer"]
                            else:
                                answer = f"Error: {resp.text}"
                        except requests.exceptions.ConnectionError:
                            answer = "Can't reach backend. Is it running on port 8000?"
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()