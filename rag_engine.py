import os
import tempfile
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever


class RAGEngine:
    def __init__(self, api_key, model="gpt-3.5-turbo", chunk_size=500, chunk_overlap=50, top_k=4):
        os.environ["OPENAI_API_KEY"] = api_key
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = None
        self.retriever = None
        self.llm = None

    def _load_file(self, uploaded_file) -> List[Document]:
        name = uploaded_file.name
        suffix = os.path.splitext(name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            loader = PyPDFLoader(tmp_path) if suffix == ".pdf" else TextLoader(tmp_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = name
            return docs
        finally:
            os.unlink(tmp_path)

    def build_index(self, uploaded_files) -> Tuple[int, int]:
        all_docs = []
        for f in uploaded_files:
            all_docs.extend(self._load_file(f))
        if not all_docs:
            raise ValueError("No content extracted from uploaded files.")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(all_docs)
        if not chunks:
            raise ValueError("No text chunks produced.")
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": self.top_k}
        )
        self.llm = ChatOpenAI(model=self.model, temperature=0)
        return len(uploaded_files), len(chunks)

    def query(self, question: str, chat_history: list) -> Tuple[str, list]:
        if self.retriever is None:
            raise RuntimeError("Index not built. Call build_index() first.")

        # Build LangChain message history
        lc_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                lc_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_history.append(AIMessage(content=msg["content"]))

        # History-aware retriever: reformulates query given chat history
        contextualize_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and the latest user question, reformulate a standalone question. Return ONLY the question, no explanation."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_prompt
        )

        # QA chain
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer the question using ONLY the context below. If the answer is not in the context, say so.\n\nContext:\n{context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        qa_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

        result = rag_chain.invoke({"input": question, "chat_history": lc_history})

        answer = result["answer"]
        source_docs = result.get("context", [])

        seen = set()
        sources = []
        for doc in source_docs:
            snippet = doc.page_content[:100]
            if snippet not in seen:
                seen.add(snippet)
                sources.append({
                    "source": doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content,
                })
        return answer, sources
