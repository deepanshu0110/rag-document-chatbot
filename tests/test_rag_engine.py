import io
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class FakeCompletions:
    def __init__(self):
        self.messages = None

    def create(self, model, messages, temperature):
        self.messages = messages
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="stub answer"))])


def test_index_retrieval_and_prompt():
    from rag_engine import RAGEngine

    doc = io.BytesIO((ROOT / "sample_docs" / "ml_overview.txt").read_bytes())
    doc.name = "ml_overview.txt"
    engine = RAGEngine(api_key="test-key", top_k=2)
    n_files, n_chunks = engine.build_index([doc])
    assert n_files == 1 and n_chunks > 0

    fake = FakeCompletions()
    engine.client = SimpleNamespace(chat=SimpleNamespace(completions=fake))
    history = [{"role": "user", "content": f"q{i}"} for i in range(10)]
    answer, sources = engine.query("What is supervised learning?", history)

    assert answer == "stub answer"
    assert sources and sources[0]["source"] == "ml_overview.txt"
    # system prompt + last 6 history messages + the new question
    assert len(fake.messages) == 8
    assert "Context:" in fake.messages[0]["content"]
