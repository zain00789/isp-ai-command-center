
from unittest.mock import patch

from langchain_core.messages import HumanMessage, AIMessage

from agents.support_graph import ai_agent


def test_account_lookup_tools_are_not_exposed():
    """The support agent must not expose customer account tools."""

    from agents import support_graph

    assert not hasattr(support_graph, "guarded_tools")
    assert not hasattr(support_graph, "get_customer_status")


def test_agent_does_not_execute_customer_lookup():
    """An LLM-generated lookup request must not execute an account tool."""

    fake_response = AIMessage(
        content="Customer verification zaroori hai."
    )

    with (
        patch(
            "agents.support_graph.hybrid_search",
            return_value=[]
        ),
       patch(
        "agents.support_graph.llm"
        ) as mock_llm,
    ):
        mock_llm.invoke.return_value = fake_response
        result = ai_agent({
            "messages": [
                HumanMessage(
                    content="Mera customer ID ISP001 hai. Status batao."
                )
            ]
        })

    assert result["messages"][0].content == (
        "Customer verification zaroori hai."
    )
    mock_llm.invoke.assert_called_once()
