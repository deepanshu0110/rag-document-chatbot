# 🤖 RAG Document Chatbot

> **Chat with your documents using AI** — upload PDFs or text files and ask questions. Powered by LangChain, FAISS, Sentence Transformers, and OpenAI.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![LangChain](https://img.shields.io/badge/LangChain-0.2%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?logo=streamlit)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 What It Does

Upload any PDF or TXT document and ask questions about its content. The chatbot:

- **Extracts and chunks** your document into searchable pieces
- **Embeds** each chunk using free local `sentence-transformers` (no extra API cost)
- **Retrieves** the most relevant chunks via FAISS similarity search
- **Generates** a precise, context-aware answer using OpenAI GPT
- **Shows sources** — every answer links back to the exact document chunks used

---

## 🏗️ Architecture

```
User uploads PDF/TXT
        │
        ▼
  Document Loader (PyPDF / TextLoader)
        │
        ▼
  RecursiveCharacterTextSplitter
  (chunk_size=500, overlap=50)
        │
        ▼
  HuggingFace Embeddings
  (all-MiniLM-L6-v2, FREE, local)
        │
        ▼
  FAISS Vector Store (in-memory)
        │
   ─────┴──────────────────────────
   │                              │
   ▼                              ▼
User Query                Retrieve Top-K Chunks
   │                              │
   └──────────────┬───────────────┘
                  ▼
          OpenAI ChatGPT
          (gpt-3.5-turbo / gpt-4o-mini / gpt-4o)
                  │
                  ▼
         Answer + Source Chunks
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/deepanshu0110/rag-document-chatbot.git
cd rag-document-chatbot
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

```bash
cp .env.example .env
# Edit .env and add your key
```

Or just enter it directly in the app sidebar.

### 5. Run the app

```bash
streamlit run app.py
```

---

## 🎛️ Features

| Feature | Details |
|---------|---------|
| **Multi-file upload** | Upload multiple PDFs and TXTs at once |
| **Free embeddings** | `all-MiniLM-L6-v2` via sentence-transformers — no embedding API cost |
| **FAISS vector search** | Fast local similarity search — no external DB |
| **Conversational memory** | Remembers last 5 turns of conversation |
| **Source citations** | Every answer shows the exact chunks retrieved |
| **Model selector** | Switch between gpt-3.5-turbo, gpt-4o-mini, gpt-4o |
| **Configurable chunking** | Adjust chunk size, overlap, and top-K retrieval |

---

## 🗂️ Project Structure

```
rag-document-chatbot/
├── app.py              # Streamlit frontend
├── rag_engine.py       # RAG pipeline (load → chunk → embed → retrieve → answer)
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
├── .gitignore
└── README.md
```

---

## 💡 Example Use Cases

- **Research papers** — "What methodology did the authors use?"
- **Legal contracts** — "What are the termination clauses?"
- **Financial reports** — "What was the revenue growth in Q3?"
- **Technical docs** — "How do I configure the authentication module?"
- **HR policies** — "What is the leave policy?"

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Orchestration | LangChain |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (FREE) |
| Vector Store | FAISS (local, in-memory) |
| LLM | OpenAI GPT (gpt-3.5-turbo / gpt-4o-mini / gpt-4o) |
| PDF Parsing | PyPDF |
| Memory | ConversationBufferWindowMemory (k=5) |

---

## 📈 Future Improvements

- [ ] Support for DOCX, CSV, and Markdown files
- [ ] Persistent FAISS index (save/load from disk)
- [ ] Local LLM support via Ollama (fully offline mode)
- [ ] Re-ranking with cross-encoders for better retrieval
- [ ] Streamlit Cloud deployment

---

## 👤 Author

**Deepanshu Garg** — Freelance Data Scientist & ML Engineer

- GitHub: [@deepanshu0110](https://github.com/deepanshu0110)
- Email: deepanshugarg35@gmail.com

---

## 📄 License

MIT License — free to use, modify, and distribute.
