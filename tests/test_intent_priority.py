
import pytest

from fastapi.testclient import TestClient

from backend.main import app
from agents.ai_service import conversations
from agents.panel_session import panel_sessions
from agents.session_manager import clear_session
from agents.intent_priority import detect_priority_intent


client = TestClient(app)


@pytest.mark.parametrize(
    "message, expected_intent, expected_action",
    [
        (
            "Mera bill kitna hai?",
            "billing",
            "verification_required",
        ),
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
def test_interrupt_panel_workflow(
    message,
    expected_intent,
    expected_action,
):
    session_id = f"priority-test-{expected_intent}"

    clear_session(session_id, conversations)

    try:
        # Start the panel workflow.
        first_response = client.post(
            "/api/v1/ai/respond",
            json={
                "session_id": session_id,
                "message": "start connection check",
            },
        )

        assert first_response.status_code == 200
        assert first_response.json()["action"] == "ask_panel"

        # Interrupt with an explicit request.
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

        # The previous panel workflow must be cleared.
        assert session_id not in panel_sessions

    finally:
        clear_session(session_id, conversations)


def test_cancellation_has_priority_over_registration():
    intent = detect_priority_intent(
        "Meri complaint cancel kar dein"
    )

    assert intent == "cancel_complaint"
