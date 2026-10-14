
from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from backend.main import app
from agents.ai_service import conversations
from agents.panel_session import panel_sessions


client = TestClient(app)


def test_rag_support_through_api():
    session_id = "rag-api-test-001"

    conversations.pop(session_id, None)
    panel_sessions.pop(session_id, None)

    retrieved_faq = [
        {
            "question": "What does a red LOS light mean?",
            "answer": (
                "A red LOS light on many fiber ONTs "
                "indicates loss of optical signal."
            ),
            "source": "keyword",
            "rank_score": 2.0,
        }
    ]

    class FakeLLM:
        def invoke(self, messages):
            # Confirm FAQ content reaches the model.
            assert any(
                "loss of optical signal" in str(msg.content)
                for msg in messages
            )

            return AIMessage(
                content=(
                    "Red LOS light optical signal loss "
                    "ka ishara hai."
                )
            )

    try:
        with (
            patch(
                "agents.ai_service.detect_intent",
                return_value="general_support",
            ),
            patch(
                "agents.support_graph.hybrid_search",
                return_value=retrieved_faq,
            ),
            patch(
                "agents.support_graph.llm",
                new=FakeLLM(),
            ),
        ):
            response = client.post(
                "/api/v1/ai/respond",
                json={
                    "session_id": session_id,
                    "message": "Router par red LOS light hai",
                },
            )

        assert response.status_code == 200

        data = response.json()

        assert data["intent"] == "general_support"
        assert data["action"] == "respond"
        assert (
            "optical signal loss"
            in data["response"].lower()
        )

    finally:
        conversations.pop(session_id, None)
        panel_sessions.pop(session_id, None)
