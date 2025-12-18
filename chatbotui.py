import streamlit as st
from chunking import MarkdownChunker
from StoringRetrieval import VectorStoreRetrival 
from LLM import QueryLLM

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(page_title="PDF RAG Chat", layout="wide")
st.title("📄 PDF Chatbot")

# -------------------------------
# Session state
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "db" not in st.session_state:
    st.session_state.db = None

if "llm" not in st.session_state:
    st.session_state.llm = QueryLLM()

if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False

# -------------------------------
# PDF upload
# -------------------------------
pdf_file = st.file_uploader("Upload a PDF", type="pdf")

# -------------------------------
# Process PDF ONCE
# -------------------------------
if pdf_file and not st.session_state.pdf_loaded:
    with st.spinner("Processing PDF..."):
        chunker = MarkdownChunker()
        chunks = chunker.convert_to_chunks(pdf_file)

        db = VectorStoreRetrival()
        db.create_db(chunks)

        st.session_state.db = db
        st.session_state.pdf_loaded = True

    st.success("PDF processed successfully!")

# -------------------------------
# Show chat history
# -------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# Chat input
# -------------------------------
query = st.chat_input("Ask a question about the PDF")

if query:
    if not st.session_state.pdf_loaded:
        st.warning("Please upload a PDF first.")
    else:
        # User message
        st.session_state.messages.append({
            "role": "user",
            "content": query
        })
        with st.chat_message("user"):
            st.write(query)

        # Retrieve context
        context = st.session_state.db.retrieve_data(query)

        # LLM call
        response = st.session_state.llm.query_llm(
            context=context,
            query=query
        )

        # Assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.content
        })
        with st.chat_message("assistant"):
            st.write(response.content)

# -------------------------------
# Clear chat
# -------------------------------
if st.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.rerun()
