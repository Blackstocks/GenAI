# worker.py
# flake8: noqa
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI


def process_query(query: str):
    print("Searching chunk", query)

    # ✅ Load embedding model and vector store dynamically every time
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

    vector_db = QdrantVectorStore.from_existing_collection(
        url="http://vector-db:6333",
        collection_name="tutorial",
        embedding=embedding_model,
    )

    search_result = vector_db.similarity_search(query=query)

    context = "\n\n".join(
        [
            f"Page Content: {result.page_content}\nPage Number: {result.metadata.get('page_label', 'N/A')}"
            for result in search_result
        ]
    )

    SYSTEM_PROMPT = f"""
    You are a helpful AI assistant who answers user queries based on the available content retrieved from a PDF file along with page_content and page_number.
    You should only answer the user based on the following context and navigate the user to open the right page number to know more.

    Context: {context}
    """

    client = OpenAI()
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )

    print(f"User: {query}\nBot: {chat_completion.choices[0].message.content}\n\n")
    return chat_completion.choices[0].message.content
