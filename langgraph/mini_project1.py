# type: ignore
import os
from typing import Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class ClassifyMessageResponse(BaseModel):
    query_type: Literal["coding", "cooking", "general"]


class CodeAccuracyResponse(BaseModel):
    accuracy: str


class RecipeQuantityResponse(BaseModel):
    quantify: str


class State(TypedDict):
    user_query: str
    llm_result: Optional[str]
    accuracy: Optional[str]
    quantify: Optional[str]
    query_type: Optional[str]


def classify_message(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are an helpful AI agent. Your job is to detect if the user's query is related to coding or cooking or general.
    Return your response as a JSON like this: {"query_type": "cooking"}

    """
    response = client.chat.completions.parse(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["query_type"] = response.choices[0].message.parsed.query_type
    return state


def general(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = "Answer the user’s general query clearly and concisely."
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def coding(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = (
        "You are a programming expert. Help the user solve the code problem."
    )
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def Cooking(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = "You are a helpful cooking agent. Answer recipie or food questions."
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def route_query(state: State) -> Literal["general", "coding", "Cooking"]:
    return f"{state['query_type']}_query"


def code_validator(state: State):
    SYSTEM_PROMPT = f"""
    Rate how accurate this code is for the user's query as a percentage.
    Output must be JSON: {{ "accuracy": "85%" }}

    Query: {state['user_query']}
    Code: {state['llm_result']}
    """
    response = client.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=CodeAccuracyResponse,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
    )
    state["accuracy"] = response.choices[0].message.parsed.accuracy
    return state


def check_code(state: State) -> Literal["coding", "__end__"]:
    try:
        accuracy = float(state["accuracy"].strip("%"))
    except Exception:
        accuracy = 0.0
    return "coding" if accuracy < 80 else "__end__"


def recipie_quantified(state: State):
    SYSTEM_PROMPT = f"""
    Convert the following cooking instructions into quantified recipe.
    Return JSON: {{ "quantify": "2 cups rice, 1 tsp salt, etc." }}

    Recipe: {state['llm_result']}
    """
    response = client.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=RecipeQuantityResponse,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
    )
    state["quantify"] = response.choices[0].message.parsed.quantify
    return state


def recipie_quantity(state: State) -> Literal["Cooking", "__end__"]:
    return "__end__" if state.get("quantify") else "Cooking"


graph_builder = StateGraph(State)
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("general", general)
graph_builder.add_node("coding", coding)
graph_builder.add_node("Cooking", Cooking)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("code_validator", code_validator)
graph_builder.add_node("check_code", check_code)
graph_builder.add_node("recipie_quantified", recipie_quantified)
graph_builder.add_node("recipie_quantity", recipie_quantity)

graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)
graph_builder.add_edge("general", END)
graph_builder.add_edge("coding", "code_validator")
graph_builder.add_conditional_edges("code_validator", check_code)
graph_builder.add_edge("Cooking", "recipie_quantified")
graph_builder.add_conditional_edges("recipie_quantified", recipie_quantity)

graph = graph_builder.compile()


def main():
    user = input("> ")
    _state: State = {
        "user_query": user,
        "llm_result": None,
        "accuracy": None,
        "quantify": None,
        "query_type": None,
    }
    graph_result = graph.invoke(_state)
    print(
        "\n🧠 Response from graph:\n",
        graph_result.get("llm_result", "accuracy", "quantify", "query_type"),
    )


if __name__ == "__main__":
    main()
