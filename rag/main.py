import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

api_key = "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"

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not set!")

print(f"✅ API key loaded: {api_key[:20]}...")

# Load PDF
pdf_path = Path(__file__).parent / "rag2.pdf"
print(f"Loading PDF from: {pdf_path}")

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
    model="text-embedding-3-large", openai_api_key=api_key
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
