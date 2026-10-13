
import re

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
)

from langgraph.graph import StateGraph, START
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import tools_condition

from llm_config import get_llm

from tools.customer_tools import (
    get_customer_status,
    get_customer_package,
)
from tools.billing_tools import get_customer_bill


# Read-only fictional account tools
tools = [
    get_customer_status,
    get_customer_package,
    get_customer_bill,
]

tool_map = {tool.name: tool for tool in tools}

llm = get_llm()
llm_with_tools = llm.bind_tools(tools)


def supplied_customer_ids(messages):
    """
    Collect IDs explicitly written by the customer.

    Only HumanMessage objects are trusted for this
    fictional demo's ID-presence check.
    """
    ids = set()

    for message in messages:
        if isinstance(message, HumanMessage):
            matches = re.findall(
                r"\bISP\d{3,}\b",
                str(message.content),
                flags=re.IGNORECASE,
            )
            ids.update(value.upper() for value in matches)

    return ids


def ai_agent(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])

    print("Agent node executed")

    if response.tool_calls:
        print(
            "Tool requested:",
            [call["name"] for call in response.tool_calls]
        )
    else:
        print("No tool requested")

    return {"messages": [response]}


def guarded_tools(state: MessagesState):
    """
    Validate each tool call before executing it.

    A model-generated customer ID cannot authorize
    its own lookup.
    """
    messages = state["messages"]
    approved_ids = supplied_customer_ids(messages)

    latest_ai_message = messages[-1]
    responses = []

    for call in latest_ai_message.tool_calls:
        tool_name = call["name"]
        tool_args = call.get("args", {})
        tool_call_id = call["id"]

        requested_id = str(
            tool_args.get("customer_id", "")
        ).upper()

        if requested_id not in approved_ids:
            result = {
                "error": "customer_id_not_supplied",
                "message": (
                    "This customer ID was not supplied "
                    "by the customer. Ask for their ID."
                ),
            }

        elif tool_name not in tool_map:
            result = {
                "error": "unknown_tool",
                "message": "Requested tool is not available.",
            }

        else:
            try:
                result = tool_map[tool_name].invoke(tool_args)
            except Exception:
                result = {
                    "error": "tool_execution_failed",
                    "message": "Lookup could not be completed.",
                }

        responses.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call_id,
                name=tool_name,
            )
        )

    return {"messages": responses}


# LangGraph workflow
workflow = StateGraph(MessagesState)

workflow.add_node("agent", ai_agent)
workflow.add_node("tools", guarded_tools)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
)

workflow.add_edge("tools", "agent")

app = workflow.compile()


if __name__ == "__main__":
    print("\nTesting guarded LangGraph workflow...\n")

    result = app.invoke(
        {
            "messages": [
                SystemMessage(
                    content=(
                        "You are a Pakistani ISP support assistant. "
                        "Reply in Roman Urdu. Never invent customer IDs. "
                        "If no customer ID is supplied, ask for it. "
                        "Use only fictional test data."
                    )
                ),
                HumanMessage(
                    content="ISP001 ka internet bill kitna hai?"
                ),
            ]
        },
        config={"recursion_limit": 10},
    )

    final_message = result["messages"][-1]

    print("\nAI Agent:")
    print(final_message.content)
