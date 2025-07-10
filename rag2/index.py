# index.py
# flake8: noqa

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI
from qdrant_client import QdrantClient


def run_indexing(pdf_path: str = "./rag2/rag2.pdf"):
    """Indexes the specified PDF into Qdrant vector store."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY not set in environment!")

    print(f"✅ API key loaded: {api_key[:20]}...")
    print(f"📄 Loading PDF from: {pdf_path}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF file not found: {pdf_path}")

    # Delete old vectors from collection if it exists
    client = QdrantClient(url="http://vector-db:6333")
    collections = client.get_collections()
    if "tutorial" in [col.name for col in collections.collections]:
        print("🧹 Deleting old collection 'tutorial'...")
        client.delete_collection(collection_name="tutorial")

    # Load and split PDF
    loader = PyPDFLoader(file_path=pdf_path)
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} pages from PDF")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)
    print(f"✅ Split into {len(split_docs)} chunks")

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
    print("✅ Created embedding model")

    # Save new embeddings
    vector_store = QdrantVectorStore.from_documents(
        documents=split_docs,
        url="http://vector-db:6333",
        collection_name="tutorial",
        embedding=embedding_model,
    )
    print("✅ Document indexing complete.")


# Optional: allows command line usage
if __name__ == "__main__":
    run_indexing()
