# type: ignore
import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class State(TypedDict):
    user_quer: str
    llm_result: optional[str]
    accuracy: optional[str]
    quantify: optional[str]
    is_coding: optional[str]
    is_cooking: optional[str]


def classify_message(state: State):
    pass


def general(state: State):
    pass


def coding(state: State):
    pass


def Cooking(state: State):
    pass


def route_query(state: State) -> LITERAL["general", "coding", "Cooking"]:
    pass


def code_validator(state: State):
    pass


def recipie_quantified(state: State):
    pass


def check_code(state: State):
    pass


def recipie_quantity(state: State):
    pass


graph_builder = StateGraph(State)
graph_builder.add_node("classify_message",classify_message)
graph_builder.add_node("general",general)
graph_builder.add_node("coding",coding)
graph_builder.add_node("Cooking",Cooking)
graph_builder.add_node("route_query",route_query)


graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edge("classify_message", route_query)
graph_builder.add_edge("general", END)
graph_builder.add_edge("coding", "code_validator")
graph_builder.add_conditional_edge("code_validator", check_code)
graph_builder.add_edge("Cooking", "recipie_quantified")
graph_builder.add_conditional_edge("recipie_quantified", recipie_quantity)

graph = graph_builder.compile()

def main():
    user = input("> ")
    _state: State = {
        user_quer: str
        llm_result: optional[str]
        accuracy: optional[str]
        quantify: optional[str]
        is_coding: optional[str]
        is_cooking: optional[str]
    }
    graph_result = graph.invoke(_state)
    print("\n🧠 Response from graph:\n", graph_result["llm_result"])


if __name__ == "__main__":
    main()

