import os
from pathlib import Path
from typing import List, Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from PyPDF2 import PdfReader

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
GENERATION_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
VECTOR_STORES: Dict[str, FAISS] = {}
CHUNK_STATS: Dict[str, List[Dict[str, Any]]] = {}


class GeminiEmbeddings:
    def __init__(self, api_key: str, model: str = EMBEDDING_MODEL):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment.")
        genai.configure(api_key=api_key)

        self.primary_model = model
        self.fallback_models = [
            "models/embedding-001",
            "embedding-001",
        ]

    def _embed(self, text: str, task_type: str) -> List[float]:
        candidate_models = [self.primary_model, *self.fallback_models]
        last_error = None

        for candidate in candidate_models:
            try:
                response = genai.embed_content(
                    model=candidate,
                    content=text,
                    task_type=task_type,
                )
                return response["embedding"]
            except Exception as exc:
                last_error = exc
                error_text = str(exc).lower()
                if "not found" not in error_text and "not supported" not in error_text:
                    raise

        raise ValueError(
            "No supported Gemini embedding model is available. "
            "Tried configured and fallback models. "
            f"Last error: {last_error}"
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text, task_type="retrieval_document") for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text, task_type="retrieval_query")

    def __call__(self, text: str) -> List[float]:
        """Compatibility shim for vectorstore paths that treat embeddings as callable."""
        return self.embed_query(text)



def _resolve_upload_path(filename: str) -> Path:
    return UPLOAD_DIR / filename


def _extract_pdf_pages(file_path: Path) -> List[Dict[str, Any]]:
    reader = PdfReader(str(file_path))
    pages = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"page": page_index, "text": text})
    return pages


def _chunk_pages(pages: List[Dict[str, Any]]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    documents: List[Document] = []
    for page in pages:
        chunks = splitter.split_text(page["text"])
        for chunk_index, chunk in enumerate(chunks, start=1):
            documents.append(Document(page_content=chunk, metadata={"page": page["page"], "chunk": chunk_index}))
    return documents


def index_document(filename: str) -> Dict[str, Any]:
    file_path = _resolve_upload_path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"Document not found: {filename}")

    pages = _extract_pdf_pages(file_path)
    if not pages:
        raise ValueError("No readable text found in the document.")

    documents = _chunk_pages(pages)
    embeddings = GeminiEmbeddings(API_KEY)
    vector_store = FAISS.from_documents(documents, embeddings)
    VECTOR_STORES[filename] = vector_store
    CHUNK_STATS[filename] = [{"page": doc.metadata["page"], "chunk": doc.metadata["chunk"]} for doc in documents]

    return {
        "filename": filename,
        "pages_indexed": len({page["page"] for page in pages}),
        "chunks_indexed": len(documents),
    }


def query_document(filename: str, question: str, k: int = 4) -> Dict[str, Any]:
    if filename not in VECTOR_STORES:
        raise ValueError("Document not indexed yet. Upload the document first.")

    vector_store = VECTOR_STORES[filename]
    docs = vector_store.similarity_search(question, k=k)
    if not docs:
        return {"answer": "No relevant context found in the document.", "sources": []}

    context_lines = []
    sources = []
    for doc in docs:
        page = doc.metadata.get("page")
        chunk = doc.metadata.get("chunk")
        citation = f"[Page {page}, Chunk {chunk}]"
        context_lines.append(f"{citation} {doc.page_content}")
        sources.append({"page": page, "chunk": chunk, "snippet": doc.page_content[:200]})

    prompt = f"""
You are an expert assistant. Use ONLY the context below to answer the question.
If the answer is not in the context, say you cannot find it in the document.
Include citations in the format [Page X, Chunk Y] in your answer.

Context:
{os.linesep.join(context_lines)}

Question: {question}
Answer:
"""
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(GENERATION_MODEL)
    response = model.generate_content(prompt)

    return {"answer": response.text, "sources": sources}
