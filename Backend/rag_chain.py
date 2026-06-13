from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY, CHAT_MODEL, TOP_K, RELEVANCE_SCORE_THRESHOLD


def get_llm():
    """Return the ChatGroq LLM instance."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=CHAT_MODEL,
        temperature=0.2,
    )


# Prompt used when relevant PDF context IS found
RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Use the following context from the
uploaded PDF to answer the user's question. If the context doesn't fully
answer the question, you may also use your own general knowledge to fill gaps.

Context from PDF:
{context}

Question: {question}

Answer:"""
)

# Prompt used when NO relevant PDF context is found (general knowledge)
GENERAL_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant. The user asked a question that is not
covered in the uploaded PDF. Answer it using your own general knowledge,
clearly and concisely.

Question: {question}

Answer:"""
)


def get_answer(question: str, vectorstore):
    """
    Hybrid RAG logic:
    1. Search the vectorstore for relevant chunks.
    2. If relevant chunks are found (score below threshold), answer using
       that context (+ general knowledge to fill gaps).
    3. If nothing relevant is found, fall back to pure general-knowledge answer.
    """
    llm = get_llm()

    # similarity_search_with_score returns (Document, distance_score)
    # Lower distance = more similar (Chroma uses L2/cosine distance)
    results = vectorstore.similarity_search_with_score(question, k=TOP_K)
    

    # Filter chunks that are "relevant enough"
    relevant_chunks = [
        doc for doc, score in results if score <= RELEVANCE_SCORE_THRESHOLD
    ]

    if relevant_chunks:
        context = "\n\n".join(chunk.page_content for chunk in relevant_chunks)
        prompt = RAG_PROMPT.format(context=context, question=question)
    else:
        prompt = GENERAL_PROMPT.format(question=question)

    response = llm.invoke(prompt)
    return response.content