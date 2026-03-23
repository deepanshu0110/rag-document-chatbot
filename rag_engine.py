"""
rag_engine.py
─────────────
Core RAG pipeline using:
  - LangChain for orchestration
  - FAISS for vector store (local, no external DB needed)
  - Sentence-Transformers for FREE embeddings (all-MiniLM-L6-v2)
  - OpenAI (gpt-3.5-turbo / gpt-4o-mini / gpt-4o) for answer generation
  - PyPDF for PDF parsing
"""

import os
import io
import tempfile
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document


class RAGEngine:
    """
    End-to-end RAG pipeline.

    Flow:
      Upload files → load → split → embed (free, local) → FAISS index
      Query → retrieve top-k chunks → LLM answer with citations
    """

    def __init__(
