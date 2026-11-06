"""
Banking Compliance Policy Chatbot Engine using LangChain, Claude & Chroma Vector DB
Retrieves compliance policy chunks via Chroma similarity search and restructures the response using an LLM.
"""

import os
from typing import Dict, Any, Optional, List

try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from core.rag_engine import PolicyRAGEngine
from guardrails.pii_masker import BankingPIIGuardrail
from guardrails.injection_defense import InjectionDefenseGuardrail
from database.encrypted_db import EncryptedBankingVault
from util.helper import restructure_with_local_engine


class BankingCompliantAgent:
    """
    RAG-powered Banking Compliance AI Agent.
    Workflow:
    1. Ingress PII Redaction & Adversarial Injection Defense
    2. Chroma Vector DB Similarity Search (Retrieves relevant policy clauses)
    3. LLM Restructuring & Synthesis (Claude / LangChain) grounded strictly in retrieved context
    4. Cites source manuals, clauses, and compliance thresholds
    """

    SYSTEM_PROMPT = """You are "BankGuard Policy Assistant", an enterprise banking regulatory intelligence agent.

YOUR TASK:
Synthesize, explain, and restructure the retrieved banking compliance clauses into a clear, professional, and authoritative answer for the user's inquiry.

STRICT RESTRUCTURING GUIDELINES:
1. Grounding: Rely strictly on the RETRIEVED BANKING POLICY CONTEXT provided below. Do not hallucinate or invent rules not present in the text.
2. Structure your response into clear executive sections:
   - 📌 **Policy Summary**: A direct 1-2 sentence executive answer to the user's question.
   - ⚖️ **Regulatory Mandates & Thresholds**: Specific legal rules, timeframes, dollar limits (e.g., $10,000 CTR, 10-day provisional credit, 43% DTI), and statutory citations (e.g., 31 CFR § 1010.311, 12 CFR § 1005.11).
   - ⚠️ **Operational Requirements / Exceptions**: Any mandatory bank actions, customer liability conditions, or non-compliance penalties.
   - 📚 **Official Source Citations**: Explicitly state the source policy document name and relevant clause.
3. Tone: Professional, authoritative, precise, and easily readable by compliance officers and bank staff.
4. Security: The user prompt was sanitized by PII guardrails. Never request or expose unmasked full card numbers or SSNs.

--- RETRIEVED BANKING POLICY CONTEXT (FROM CHROMA VECTOR DB) ---
{policy_context}
-----------------------------------------------------------------
"""

    def __init__(
        self,
        vault: EncryptedBankingVault,
        rag_engine: Optional[PolicyRAGEngine] = None,
        anthropic_api_key: Optional[str] = None
    ):
        self.vault = vault
        self.rag_engine = rag_engine or PolicyRAGEngine()
        self.pii_guardrail = BankingPIIGuardrail()
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")

        # Initialize Claude via LangChain
        self.llm = None
        if LANGCHAIN_AVAILABLE and self.api_key and not self.api_key.startswith("your_"):
            try:
                self.llm = ChatAnthropic(
                    model="claude-sonnet-5-5",
                    anthropic_api_key=self.api_key,
                    max_tokens_to_sample=1024
                )
            except Exception as e:
                print(f"Warning: Could not initialize ChatAnthropic: {e}")

    def process_turn(self, raw_user_message: str, customer_id: str = "CUST-88412") -> Dict[str, Any]:
        """
        Executes complete RAG lifecycle:
        Stage 1: Injection Defense
        Stage 2: PII Ingress Scrubbing
        Stage 3: Chroma Vector DB Similarity Search
        Stage 4: LLM Restructuring & Synthesis
        Stage 5: Audit Ledger Chaining
        """
        # 1. Adversarial Guardrail
        is_safe, threats = InjectionDefenseGuardrail.evaluate_prompt(raw_user_message)
        if not is_safe:
            return {
                "reply": "⚠️ [SECURITY EXCEPTION] Adversarial command intercepted. Compliance queries must conform to standard policy research formats.",
                "retrieved_sources": [],
                "pii_detected": [],
                "is_blocked": True
            }

        # 2. PII Guardrail
        sanitized_prompt, pii_entities = self.pii_guardrail.mask_and_tokenize(raw_user_message)

        # 3. Chroma Vector DB Similarity Search
        retrieved_chunks = self.rag_engine.similarity_search(sanitized_prompt, top_k=3)

        # Format context block for LLM prompt
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            context_blocks.append(
                f"[Document {idx}: {chunk['source']} | Similarity Match: {chunk['similarity_score']}%]\n"
                f"{chunk['content']}"
            )
        formatted_context = "\n\n".join(context_blocks) if context_blocks else "No matching regulatory manual clauses found."
        
        print(f"DEBUG: Retrieved {len(retrieved_chunks)} chunks for prompt: '{sanitized_prompt}'")
        
        # 4. Restructure Response using LLM
        if self.llm and retrieved_chunks:
            try:
                system_instruction = self.SYSTEM_PROMPT.format(policy_context=formatted_context)
                messages = [
                    SystemMessage(content=system_instruction),
                    HumanMessage(content=sanitized_prompt)
                ]
                claude_response = self.llm.invoke(messages)
                
                # ==============================================================
                # FIX: EXTRACT PLAIN TEXT FROM CLAUDE'S RAW BLOCKS RESPONSE
                # ==============================================================
                raw_content = claude_response.content
                
                if isinstance(raw_content, list):
                    clean_text = ""
                    for block in raw_content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            clean_text += block.get("text", "")
                    reply_text = clean_text
                else:
                    reply_text = str(raw_content)
                
            except Exception as err:
                print(f"LLM generation failed, running local RAG synthesizer: {err}")
                reply_text = restructure_with_local_engine(sanitized_prompt, retrieved_chunks)
        else:
            # Local high-fidelity RAG restructuring engine when operating offline
            reply_text = restructure_with_local_engine(sanitized_prompt, retrieved_chunks)

        print(f"DEBUG: Final synthesized reply LLM: '{reply_text}'")
        print(f"DEBUG: PII entities detected:'{pii_entities}'")
        print(f"================================")
    
        # 5. Audit Logging
        self.vault.log_audit_event(
            actor="COMPLIANCE_USER",
            action="RAG_POLICY_SYNTHESIS",
            details={
                "retrieved_chunks": len(retrieved_chunks),
                "top_source": retrieved_chunks[0]["source"] if retrieved_chunks else "None",
                "similarity_score": retrieved_chunks[0]["similarity_score"] if retrieved_chunks else 0
            }
        )

        return {
            "reply": reply_text,
            "retrieved_sources": retrieved_chunks,
            "pii_detected": pii_entities,
            "is_blocked": False
        }
