# RAG Document Chatbot
[![CI](https://github.com/deepanshu0110/rag-document-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/deepanshu0110/rag-document-chatbot/actions)


![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-green?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

Upload any PDF or TXT and ask questions. Uses free local embeddings, FAISS vector search, and OpenAI GPT for answers with source citations.

---

## Business Problem

Professionals waste hours scanning long documents. This tool lets anyone ask plain-English questions and get precise, cited answers in seconds — from contracts, reports, manuals, or research papers.

---

## Architecture

```
Upload PDF/TXT → Chunk → Embed (free, local) → FAISS → Query → OpenAI GPT → Answer + Citations
```

---

## Key Features

| Feature | Detail |
|---|---|
| Free embeddings | all-MiniLM-L6-v2 via sentence-transformers — no API cost |
| Local vector search | FAISS in-memory — no external database |
| Conversational memory | Remembers last 5 turns |
| Source citations | Every answer links to source chunks |
| Model selector | Switch between gpt-3.5-turbo, gpt-4o-mini, gpt-4o |

---

## Use Cases

- Legal contracts — "What are the termination clauses?"
- Financial reports — "What was Q3 revenue growth?"
- Research papers — "What methodology did the authors use?"
- HR policies — "What is the leave policy?"

---

## Quickstart

```bash
git clone https://github.com/deepanshu0110/rag-document-chatbot.git
cd rag-document-chatbot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your OpenAI API key
streamlit run app.py
```

---

## Tech Stack

Python · LangChain · FAISS · sentence-transformers · OpenAI · PyPDF · Streamlit

---

## Roadmap

- [ ] DOCX, CSV, Markdown support
- [ ] Persistent FAISS index
- [ ] Ollama local LLM (fully offline)
- [ ] Streamlit Cloud deployment

---

## Author

**Deepanshu Garg** — Freelance Data Scientist
- GitHub: [@deepanshu0110](https://github.com/deepanshu0110)
- Hire: [freelancer.com/u/deepanshu0110](https://www.freelancer.com/u/deepanshu0110)

MIT License