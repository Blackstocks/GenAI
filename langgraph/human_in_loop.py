# type: ignore
import os
import requests
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt

from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

tools = []


@tool
def human_assistence(query: str) -> str:
    """Request assistance from a human"""
    human_response = interrupt(
        {"query", querry}
    )  # this saves the state in DB and kills the graph
    return human_response["data"]


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = init_chat_model(model_provider="openai", model="gpt-4.1-nano")
llm_with_tools = llm.bind_tools(tools)


def chat_bot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


tool_node = ToolNode(tools=tools)
graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_node("tools", tool_node)


graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges("chat_bot", tools_condition)
graph_builder.add_edge("tools", "chat_bot")
graph_builder.add_edge("chat_bot", END)


def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


def main():
    # mongodb://<username>:<pass>@<host>:<port>
    DB_URI = "mongodb://admin:admin@mongodb:27017"
    # thread_id
    config = {"configurable": {"thread_id": 100}}
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        graph_with_mongo = create_chat_graph(mongo_checkpointer)
        query = input("> ")
        state = State(messages=[{"role": "user", "content": query}])
        # result = graph.invoke(state)
        # print("result", result)
        for event in graph_with_mongo.stream(state, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


main()
