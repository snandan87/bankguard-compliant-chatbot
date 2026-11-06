"""
BankGuard - Banking Compliance Policy AI Assistant (Streamlit UI)
Powered by LangChain, Claude & Chroma Vector DB.
Focuses purely on banking regulatory compliance policies (BSA/AML, Reg E, FDIC, Lending Rules).
"""

import streamlit as st

from util.config import COMPLIANCE_STANDARDS
from database.encrypted_db import EncryptedBankingVault
from core.rag_engine import PolicyRAGEngine
from core.chatbot import BankingCompliantAgent

st.set_page_config(
    page_title="BankGuard - POC",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "vault" not in st.session_state:
    st.session_state.vault = EncryptedBankingVault()

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = PolicyRAGEngine()

if "agent" not in st.session_state:
    st.session_state.agent = BankingCompliantAgent(
        st.session_state.vault, 
        rag_engine=st.session_state.rag_engine
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Welcome to the **BankGuard Banking Compliance Policy Assistant**.\n\n"
                "I process, interpret, and cite official banking compliance policies grounded strictly "
                "in our **Chroma Vector Database** (BSA/AML, Regulation E, FDIC Insurance Limits, "
                "Consumer Lending & Credit Guidelines, and PCI-DSS controls).\n\n"
                "Ask any regulatory question below to query indexed compliance policy manuals."
            ),
            "sources": []
        }
    ]

st.title("⚖️ Banking Compliance Policy Assistant")
st.caption("Chroma Vector DB Powered Semantic Search & Policy Intelligence (BSA/AML · Regulation E · FDIC · Lending Rules)")

with st.expander("📄 Upload Supplemental Compliance Policy PDF into Chroma Vector DB", expanded=False):
    col_upload, col_stats = st.columns([2, 1])
    with col_upload:
        uploaded_pdf = st.file_uploader(
            "Upload Banking Policy Document (PDF or TXT)",
            type=["pdf", "txt"],
            help="Extracts text, generates semantic chunks, and stores vector embeddings in Chroma DB."
        )
        if uploaded_pdf is not None:
            if st.button("Chunk & Index Document", type="primary"):
                with st.spinner("Processing PDF and updating Chroma Vector DB..."):
                    file_bytes = uploaded_pdf.read()
                    filename = uploaded_pdf.name
                    extracted_text = st.session_state.rag_engine.extract_text_from_pdf(file_bytes, filename)
                    chunks_added = st.session_state.rag_engine.index_policy_document(filename, extracted_text)
                    st.success(f"Indexed '{filename}': {chunks_added} chunks stored in Chroma Vector DB!")
                    st.rerun()

    with col_stats:
        chunk_count = st.session_state.rag_engine.get_chunk_count()
        st.metric(label="Indexed Policy Chunks", value=f"{chunk_count} Chunks")
        st.caption("Active Collection: `banking_compliance_policies`")

st.divider()

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"📚 Retrieved Compliance Policy Context ({len(msg['sources'])} clauses from Chroma DB)"):
                for idx, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**Source {idx}:** `{src.get('source')}` (Similarity Match: **{src.get('similarity_score')}%**)")
                    st.info(src.get("content", ""))

if user_prompt := st.chat_input("Ask a banking compliance question (e.g., What is the cash CTR reporting threshold?)..."):
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching Chroma Vector DB & retrieving compliance clauses..."):
            result = st.session_state.agent.process_turn(user_prompt)
            st.markdown(result["reply"])
            if result.get("retrieved_sources"):
                with st.expander(f"📚 Retrieved Compliance Policy Context ({len(result['retrieved_sources'])} clauses from Chroma DB)"):
                    for idx, src in enumerate(result["retrieved_sources"], 1):
                        st.markdown(f"**Source {idx}:** `{src.get('source')}` (Similarity Match: **{src.get('similarity_score')}%**)")
                        st.info(src.get("content", ""))

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result["reply"],
                "sources": result.get("retrieved_sources", [])
            })