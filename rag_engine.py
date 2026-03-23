import os
import tempfile
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document


class RAGEngine:

    def __init__(
        self,
        api_key,
        model="gpt-3.5-turbo",
        chunk_size=500,
        chunk_overlap=50,
        top_k=4,
    ):
        os.environ["OPENAI_API_KEY"] = api_key
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = None
        self.chain = None

    def _load_file(self, uploaded_file):
        name = uploaded_file.name
        suffix = os.path.splitext(name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(tmp_path)
            else:
                loader = TextLoader(tmp_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = name
            return docs
        finally:
            os.unlink(tmp_path)

    def build_index(self, uploaded_files):
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
        llm = ChatOpenAI(model=self.model, temperature=0)
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
            k=5,
        )
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.top_k},
            ),
            memory=memory,
            return_source_documents=True,
            verbose=False,
        )
        return len(uploaded_files), len(chunks)

    def query(self, question, chat_history):
        if self.chain is None:
            raise RuntimeError("Index not built. Call build_index() first.")
        lc_history = []
        for i in range(0, len(chat_history) - 1, 2):
            if i + 1 < len(chat_history):
                lc_history.append((
                    chat_history[i]["content"],
                    chat_history[i + 1]["content"],
                ))
        result = self.chain({"question": question, "chat_history": lc_history})
        answer = result["answer"]
        source_docs = result.get("source_documents", [])
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
