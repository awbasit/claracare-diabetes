import uuid
from datetime import UTC, datetime
from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph

from app.core.config import get_settings
from app.interview.graph.state import InterviewState


async def _noop_node(state: InterviewState) -> dict[str, Any]:
    return {}


def _build_test_graph(checkpointer: AsyncPostgresSaver) -> Any:
    graph = StateGraph(InterviewState)
    graph.add_node("noop", _noop_node)
    graph.add_edge(START, "noop")
    graph.add_edge("noop", END)
    return graph.compile(checkpointer=checkpointer)


async def test_checkpointer_state_persists_across_a_new_saver_instance() -> None:
    """Simulates a process restart: one AsyncPostgresSaver/connection writes a
    checkpoint under a thread_id, then a brand new saver instance (a fresh
    psycopg connection, standing in for a new process) reads it back from
    Postgres — proving InterviewState round-trips through the database
    rather than living only in that first instance's memory.

    Uses a throwaway single-node graph (not build_interview_graph) so this
    test exercises the checkpointer/InterviewState persistence mechanism in
    isolation, independent of the interview graph's own business nodes
    (covered separately in test_interview_graph.py).
    """
    dsn = get_settings().psycopg_database_url
    session_id = uuid.uuid4()
    patient_id = uuid.uuid4()
    config = {"configurable": {"thread_id": str(session_id)}}
    initial_state: InterviewState = {
        "session_id": session_id,
        "patient_id": patient_id,
        "intent": "routine_checkin",
        "assessment": None,
        "turns": [{"role": "agent", "content": "hello", "timestamp": datetime.now(UTC)}],
        "pending_questions": ["how are you feeling today?"],
        "resolved_this_session": [],
        "candidate_facts": [],
    }

    async with AsyncPostgresSaver.from_conn_string(dsn) as saver:
        compiled = _build_test_graph(saver)
        await compiled.ainvoke(initial_state, config)

    try:
        async with AsyncPostgresSaver.from_conn_string(dsn) as restarted_saver:
            restarted_graph = _build_test_graph(restarted_saver)
            snapshot = await restarted_graph.aget_state(config)

            assert snapshot.values["session_id"] == session_id
            assert snapshot.values["patient_id"] == patient_id
            assert snapshot.values["intent"] == "routine_checkin"
            assert snapshot.values["pending_questions"] == ["how are you feeling today?"]
            assert len(snapshot.values["turns"]) == 1
            assert snapshot.values["turns"][0]["content"] == "hello"
    finally:
        async with AsyncPostgresSaver.from_conn_string(dsn) as cleanup_saver:
            await cleanup_saver.adelete_thread(str(session_id))
