from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.interview.graph.nodes import (
    ask_question,
    check_sufficiency,
    classify_intent,
    load_context,
    receive_answer,
    summarize,
)
from app.interview.graph.state import InterviewState


def build_interview_graph(checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
    """Wires the routing skeleton: classify_intent -> load_context ->
    ask_question <-> receive_answer, looping until check_sufficiency routes
    to summarize. ask_question/receive_answer are stub pass-throughs in this
    milestone (see nodes.py) — Prompt 2 replaces their bodies without
    changing this wiring.

    State persists across invocations keyed by `thread_id` (set to the
    interview session's id) via the Postgres checkpointer passed in.
    """
    graph = StateGraph(InterviewState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("load_context", load_context)
    graph.add_node("ask_question", ask_question)
    graph.add_node("receive_answer", receive_answer)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "load_context")
    graph.add_edge("load_context", "ask_question")
    graph.add_edge("ask_question", "receive_answer")
    graph.add_conditional_edges(
        "receive_answer",
        check_sufficiency,
        {"continue": "ask_question", "sufficient": "summarize"},
    )
    graph.add_edge("summarize", END)

    return graph.compile(checkpointer=checkpointer)
