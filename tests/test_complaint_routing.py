
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from agents.ai_service import conversations
from agents.panel_session import panel_sessions


client = TestClient(app)


def test_complaint_priority_over_connection_issue():
    session_id = "complaint-priority-test"

    conversations.pop(session_id, None)
    panel_sessions.pop(session_id, None)

    try:
        with patch(
            "agents.ai_service.detect_intent",
            return_value="connection_issue"
        ):
            response = client.post(
                "/api/v1/ai/respond",
                json={
                    "session_id": session_id,
                    "message": (
                        "Mera internet nahi chal raha, "
                        "meri complaint register kar dein."
                    )
                }
            )

        assert response.status_code == 200

        data = response.json()

        assert data["intent"] == "new_complaint"
        assert data["action"] == "start_complaint"

        assert "verification" in data["response"].lower()
        assert "register nahi hui" in data["response"].lower()

    finally:
        conversations.pop(session_id, None)
        panel_sessions.pop(session_id, None)
