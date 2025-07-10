# index.py

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


def run_indexing():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY not set in environment!")

    print(f"✅ API key loaded: {api_key[:20]}...")

    # Load PDF
    pdf_path = Path(__file__).parent / "rag2.pdf"
    print(f"📄 Loading PDF from: {pdf_path}")

    if not pdf_path.exists():
        raise FileNotFoundError(f"❌ PDF file not found: {pdf_path}")

    loader = PyPDFLoader(file_path=str(pdf_path))
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} pages from PDF")

    # Chunk text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)
    print(f"✅ Split into {len(split_docs)} chunks")

    # Embeddings
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )
    print("✅ Created embedding model")

    # Qdrant Vector Store
    vector_store = QdrantVectorStore.from_documents(
        documents=split_docs,
        url="http://vector-db:6333",
        collection_name="tutorial",
        embedding=embedding_model,
    )
    print("✅ Document indexing complete.")


# Optional: allows standalone use
if __name__ == "__main__":
    run_indexing()
