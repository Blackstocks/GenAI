# flake8: naqo
# type: ignore
import os
from typing import Optional
from langchain_core.runnables.utils import is_async_generator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal


load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class ClassifyMessageResponse(BaseModel):
    is_coding_question: bool


class CodeAccuracyResponse(BaseModel):
    accuracy_percentage: str


class State(TypedDict):
    user_query: str
    llm_result: Optional[str]
    accuracy_percentage: Optional[str]
    is_coding_question: Optional[bool]


def classify_message(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is related to coding question or not.
    Return the response in specified JSON boolean only.
    """

    llm_response = client.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyMessageResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    is_coding_question = llm_response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question
    return state


def general_query(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = f"""
    You are a helpful AI assistant who answers user queries based on the question asked.
    """
    llm_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    result = llm_response.choices[0].message.content
    state["llm_result"] = result
    return state


def coding_query(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are a coding expert agent
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def code_validation_query(state: State):
    query = state["user_query"]
    llm_code = state["llm_result"]

    SYSTEM_PROMPT = """
    You are expert in calculating accuracy of the code according to the question.
    return the accuracy percentage.
    User Querry : {query}
    code: {llm_code}
    """

    response = client.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=CodeAccuracyResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["accuracy_percentage"] = response.choices[
        0
    ].message.parsed.accuracy_percentage
    return state


def route_query(state: State) -> Literal["general_query", "coding_query"]:
    is_coding = state["is_coding_question"]
    if is_coding:
        return "coding_query"
    return "general_query"


# def check_accuracy(state: State) -> Literal["coding_query", "__end__"]:
#     accuracy_str = state["accuracy_percentage"]
#     print(accuracy_str)
#     try:
#         accuracy = float(accuracy_str.replace("%", "").strip())
#     except (ValueError, TypeError):
#         accuracy = 0.0

#     return "coding_query" if accuracy < 90 else "__end__"


def check_accuracy(state: State):
    if float(state["accuracy_percentage"].strip("%")) < 80:
        print(state["accuracy_percentage"])
        return "coding_query"
    else:
        return END


graph_builder = StateGraph(State)
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("code_validation_query", code_validation_query)

graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)
graph_builder.add_edge("general_query", END)
graph_builder.add_edge("coding_query", "code_validation_query")
graph_builder.add_conditional_edges("code_validation_query", check_accuracy)


# Compile the graph
graph = graph_builder.compile()


def main():
    user = input("> ")
    _state: State = {
        "user_query": user,
        "llm_result": None,
        "accuracy_percentage": None,
        "is_coding_question": None,
    }
    graph_result = graph.invoke(_state)
    # print("\n🧠 Response from graph:\n", graph_result["llm_result"])
    print(graph_result)


if __name__ == "__main__":
    main()
