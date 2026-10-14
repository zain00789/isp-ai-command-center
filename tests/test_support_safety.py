
from unittest.mock import patch

from langchain_core.messages import HumanMessage, AIMessage

from agents.support_graph import app


def test_support_agent_receives_safety_instructions():

    class FakeLLM:
        def invoke(self, messages):
            system_text = " ".join(
                str(msg.content)
                for msg in messages
                if msg.type == "system"
            ).lower()

            assert "factory reset" in system_text
            assert "firmware" in system_text
            assert "isp" in system_text

            return AIMessage(
                content="Aap ISP support team se rabta karein."
            )

    with (
        patch(
            "agents.support_graph.hybrid_search",
            return_value=[]
        ),
        patch(
            "agents.support_graph.llm",
            new=FakeLLM()
        ),
    ):
        result = app.invoke({
            "messages": [
                HumanMessage(
                    content=(
                        "Maine router restart kar liya, "
                        "lekin Wi-Fi abhi bhi slow hai."
                    )
                )
            ]
        })

    assert result["messages"][-1].content


def test_support_agent_has_no_account_tools():
    assert "tools" not in app.nodes
