# graph.py

# Every node takes the state, reads it, and updates it for the next node
import os
from typing import Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Get the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not set in environment!")

# Initialize OpenAI client with the API key
client = OpenAI(api_key=api_key)


# Define the structure of the state
class State(TypedDict):
    query: str
    llm_result: Optional[str]


# Define the chatbot node
def chat_bot(state: State) -> State:
    query = state["query"]
    llm_response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use gpt-4 or gpt-4o if you have access
        messages=[
            {"role": "user", "content": query},
        ],
    )
    result = llm_response.choices[0].message.content
    state["llm_result"] = result
    return state


# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

# Compile the graph
graph = graph_builder.compile()


# Run the graph with user input
def main():
    user = input("> ")
    _state: State = {"query": user, "llm_result": None}
    graph_result = graph.invoke(_state)
    print("\n🧠 Response from graph:\n", graph_result["llm_result"])


if __name__ == "__main__":
    main()
