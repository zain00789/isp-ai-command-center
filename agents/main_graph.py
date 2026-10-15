
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from agents.intent_router import detect_intent
from agents.panel_session import (
    handle_panel_conversation,
    panel_sessions,
)
from agents.ai_service import process_customer_message


class ISPState(TypedDict, total=False):
    message: str
    session_id: str
    intent: str
    response: str
    action: str


def classify_intent(state: ISPState) -> dict:
    """Identify what the customer wants."""

    message = state["message"]
    session_id = state["session_id"]

    # Continue an existing panel conversation without
    # calling the intent model again.
    if session_id in panel_sessions:
        return {"intent": "connection_issue"}

    # Identify common connection problems.
    connection_keywords = [
        "internet nahi chal",
        "net nahi chal",
        "internet band",
        "net band",
        "internet slow",
        "net slow",
        "connection problem",
        "connection issue",
        "wifi nahi chal",
        "wifi band",
        "no internet",
        "internet not working",
    ]

    if any(word in message.lower() for word in connection_keywords):
        return {"intent": "connection_issue"}

    # Explicit testing command.
    if message.strip().lower() == "start connection check":
        return {"intent": "connection_issue"}

    try:
        intent = detect_intent(message)
    except Exception:
        intent = "unclear"

    return {"intent": intent}


def route_intent(state: ISPState) -> str:
    """Choose the correct workflow."""

    if state["intent"] == "connection_issue":
        return "panel"

    return "support"


def handle_panel(state: ISPState) -> dict:
    """Collect panel and account information."""

    session_id = state["session_id"]
    message = state["message"]

    if message.strip().lower() == "start connection check":
        panel_sessions.pop(session_id, None)

    result = handle_panel_conversation(
        message=message,
        session_id=session_id,
    )

    return {
        "response": result["response"],
        "action": result["stage"],
    }


def handle_support(state: ISPState) -> dict:
    """Use the existing AI service for other requests."""

    result = process_customer_message(
        message=state["message"],
        session_id=state["session_id"],
    )

    return {
        "response": result["response"],
        "action": result["action"],
        "intent": result["intent"],
    }


workflow = StateGraph(ISPState)

workflow.add_node("intent_router", classify_intent)
workflow.add_node("panel", handle_panel)
workflow.add_node("support", handle_support)

workflow.add_edge(START, "intent_router")

workflow.add_conditional_edges(
    "intent_router",
    route_intent,
    {
        "panel": "panel",
        "support": "support",
    },
)

workflow.add_edge("panel", END)
workflow.add_edge("support", END)

app = workflow.compile()


if __name__ == "__main__":

    session_id = "main-graph-test-001"

    messages = [
        "Mera internet nahi chal raha",
        "Jazz",
        "ISP001",
    ]

    for message in messages:
        result = app.invoke(
            {
                "message": message,
                "session_id": session_id,
            }
        )

        print("\nCustomer:", message)
        print("Intent:", result["intent"])
        print("AI:", result["response"])
        print("Action:", result["action"])
