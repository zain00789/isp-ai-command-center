
from fastapi.testclient import TestClient

from backend.main import app
from agents.ai_service import conversations
from agents.panel_session import panel_sessions
from agents.session_manager import clear_session


client = TestClient(app)


def test_panel_conversation_can_be_interrupted():
    session_id = "panel-interruption-test"

    clear_session(session_id, conversations)

    try:
        # Start panel selection without invoking the LLM.
        first_response = client.post(
            "/api/v1/ai/respond",
            json={
                "session_id": session_id,
                "message": "start connection check"
            }
        )

        assert first_response.status_code == 200
        assert first_response.json()["action"] == "ask_panel"
        assert session_id in panel_sessions

        # Customer changes their request.
        second_response = client.post(
            "/api/v1/ai/respond",
            json={
                "session_id": session_id,
                "message": "Meri complaint register kar dein"
            }
        )

        assert second_response.status_code == 200

        data = second_response.json()

        assert data["intent"] == "new_complaint"
        assert data["action"] == "start_complaint"
        assert "register nahi hui" in data["response"].lower()

        # Panel workflow must be cleared.
        assert session_id not in panel_sessions

    finally:
        clear_session(session_id, conversations)
