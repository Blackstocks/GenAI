import os
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

api_key = "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"
client = OpenAI(api_key=api_key)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=api_key
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="tutorial",
    embedding=embedding_model
)

query = input(">>> ")

search_result = vector_db.similarity_search(
    query=query
)

# print("search_result:", search_result)

# Fixed: Correct f-string syntax
context = "\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}" for result in search_result])

# Fixed: Use f-string to insert context into system prompt
SYSTEM_PROMPT = f"""
You are a helpful AI assistant who answers user queries based on the available content retrieved from a PDF file along with page_content and page_number.
You should only answer the user based on the following context and navigate the user to open the right page number to know more.

Context: {context}
"""

chat_completion = client.chat.completions.create(
    model="gpt-4o-mini",  # Fixed: Use valid model name
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
)

print(f"Bot: {chat_completion.choices[0].message.content}")
