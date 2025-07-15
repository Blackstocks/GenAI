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

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")


@tool()
def get_weather(city: str):
    """This tool return the weather data of the given city"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The Weather in {city} is {response.text}"
    return "Something went wrong"


tools = [get_weather]


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = init_chat_model(model_provider="openai", model="gpt-4.1-nano")
llm_with_tools = llm.bind_tools(tools)


def chat_bot(state: State):
    # message = llm.invoke(state["messages"])
    message = llm_with_tools.invoke(state["messages"])
    return {"messages": [message]}


graph_builder = StateGraph(State)
graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()


def main():
    user_query = input("> ")
    state = State(messages=[{"role": "user", "content": user_query}])
    # result = graph.invoke(state)
    # print("result", result)
    for event in graph.stream(state, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()


main()
