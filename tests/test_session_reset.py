
from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage

from backend.main import app
from agents.ai_service import conversations
from agents.panel_session import panel_sessions
from agents.session_manager import (
    clear_session,
    session_last_activity,
)


client = TestClient(app)


def test_session_reset_clears_history_and_panel():
    session_id = "reset-test-001"

    conversations[session_id] = [
        HumanMessage(content="Mera Wi-Fi slow hai")
    ]

    panel_sessions[session_id] = {
        "stage": "ask_account",
        "panel": "jazz",
    }

    session_last_activity[session_id] = 1000

    try:
        response = client.post(
            "/api/v1/ai/respond",
            json={
                "session_id": session_id,
                "message": "new conversation",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["intent"] == "session_reset"
        assert data["action"] == "session_reset"

        assert session_id not in conversations
        assert session_id not in panel_sessions
        assert session_id not in session_last_activity

    finally:
        clear_session(session_id, conversations)


def test_reset_does_not_affect_other_sessions():
    first_session = "reset-test-customer-1"
    second_session = "reset-test-customer-2"

    conversations[first_session] = [
        HumanMessage(content="First customer")
    ]

    conversations[second_session] = [
        HumanMessage(content="Second customer")
    ]

    try:
        response = client.post(
            "/api/v1/ai/respond",
            json={
                "session_id": first_session,
                "message": "start over",
            },
        )

        assert response.status_code == 200
        assert first_session not in conversations

        assert second_session in conversations

        assert (
            conversations[second_session][0].content
            == "Second customer"
        )

    finally:
        clear_session(first_session, conversations)
        clear_session(second_session, conversations)
