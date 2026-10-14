
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState

from llm_config import get_llm


# SECURITY:
# Account-specific tools are intentionally disabled.
#
# Do NOT import or bind:
# - get_customer_status
# - get_customer_package
# - get_customer_bill
#
# They must not be reconnected until the backend
# provides trusted, account-scoped authorization.


llm = get_llm()


def ai_agent(state: MessagesState):
    """
    Respond to general support questions without
    accessing customer account information.
    """

    response = llm.invoke(state["messages"])

    return {"messages": [response]}


workflow = StateGraph(MessagesState)

workflow.add_node("agent", ai_agent)

workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

app = workflow.compile()


if __name__ == "__main__":
    print("\nTesting support agent without account tools...\n")

    result = app.invoke(
        {
            "messages": [
                SystemMessage(
                    content=(
                        "You are a Pakistani ISP support assistant. "
                        "Reply in simple Roman Urdu. "
                        "You can provide general troubleshooting help. "
                        "Never invent customer account information. "
                        "Never claim to have checked a customer's account. "
                        "Account lookups require verified authorization."
                    )
                ),
                HumanMessage(
                    content="Mera Wi-Fi signal weak hai."
                ),
            ]
        }
    )

    print("AI Agent:")
    print(result["messages"][-1].content)
