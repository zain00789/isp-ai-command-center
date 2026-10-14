
import pytest

from fastapi.testclient import TestClient

from backend.main import app
from agents.ai_service import conversations
from agents.session_manager import clear_session


client = TestClient(app)


@pytest.mark.parametrize(
    "message, expected_intent, expected_action",
    [
        ("Mera bill kitna hai?", "billing", "verification_required"),
        (
            "Meri complaint ka status bata dein",
            "ticket_status",
            "ticket_status_unavailable",
        ),
        (
            "Meri complaint cancel kar dein",
            "cancel_complaint",
            "cancellation_unavailable",
        ),
        (
            "Meri complaint register kar dein",
            "new_complaint",
            "start_complaint",
        ),
    ],
)
def test_priority_intent_without_panel(
    message,
    expected_intent,
    expected_action,
):
    session_id = f"no-panel-{expected_intent}"
    clear_session(session_id, conversations)

    try:
        response = client.post(
            "/api/v1/ai/respond",
            json={
                "session_id": session_id,
                "message": message,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["intent"] == expected_intent
        assert data["action"] == expected_action

    finally:
        clear_session(session_id, conversations)
