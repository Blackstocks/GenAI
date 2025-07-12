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
    You are a helpful AI agent. Your job is to detect if the user's query is related to coding or cooking or general.
    Return your response as a JSON like this: {"query_type": "cooking"}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        response_format={"type": "json_object"},
    )
    import json

    parsed_response = json.loads(response.choices[0].message.content)
    state["query_type"] = parsed_response["query_type"]
    return state


def general(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = "Answer the user's general query clearly and concisely."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def cooking(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = "You are a helpful cooking agent. Answer recipe or food questions."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def route_query(
    state: State,
) -> Literal["general", "coding", "cooking"]:
    return state["query_type"]


def code_validator(state: State):
    SYSTEM_PROMPT = f"""
    Rate how accurate this code is for the user's query as a percentage.
    Output must be JSON: {{ "accuracy": "85%" }}

    Query: {state['user_query']}
    Code: {state['llm_result']}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
        response_format={"type": "json_object"},
    )

    import json

    parsed_response = json.loads(response.choices[0].message.content)
    state["accuracy"] = parsed_response["accuracy"]
    return state


def check_code(state: State) -> Literal["coding", "__end__"]:
    try:
        accuracy = float(state["accuracy"].strip("%"))
    except Exception:
        accuracy = 0.0
    return "coding" if accuracy < 80 else "__end__"


def recipe_quantified(state: State):
    SYSTEM_PROMPT = f"""
    Convert the following cooking instructions into quantified recipe.
    Return JSON: {{ "quantify": "2 cups rice, 1 tsp salt, etc." }}

    Recipe: {state['llm_result']}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}],
        response_format={"type": "json_object"},
    )

    import json

    parsed_response = json.loads(response.choices[0].message.content)
    state["quantify"] = parsed_response["quantify"]
    return state


def recipe_quantity(
    state: State,
) -> Literal["cooking", "__end__"]:
    return "__end__" if state.get("quantify") else "cooking"


graph_builder = StateGraph(State)
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("general", general)
graph_builder.add_node("coding", coding)
graph_builder.add_node("cooking", cooking)
graph_builder.add_node("code_validator", code_validator)
graph_builder.add_node("recipe_quantified", recipe_quantified)


graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)
graph_builder.add_edge("general", END)
graph_builder.add_edge("coding", "code_validator")
graph_builder.add_conditional_edges("code_validator", check_code)
graph_builder.add_edge("cooking", "recipe_quantified")
graph_builder.add_conditional_edges("recipe_quantified", recipe_quantity)

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
    print("\n🧠 Response from graph:")
    print(f"Result: {graph_result.get('llm_result', 'No result')}")
    print(f"Accuracy: {graph_result.get('accuracy', 'N/A')}")
    print(f"Quantify: {graph_result.get('quantify', 'N/A')}")
    print(f"Query Type: {graph_result.get('query_type', 'N/A')}")


if __name__ == "__main__":
    main()
