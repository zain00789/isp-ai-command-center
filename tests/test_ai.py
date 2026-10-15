
from fastapi.testclient import TestClient

from backend.main import app
from agents.panel_session import panel_sessions


client = TestClient(app)


def test_ai_panel_conversation():
    session_id = "automated-panel-test-001"

    # Reset test session before starting
    panel_sessions.pop(session_id, None)

    # Message 1: Report internet problem
    response1 = client.post(
        "/api/v1/ai/respond",
        json={
            "session_id": session_id,
            "message": "Mera internet nahi chal raha",
        },
    )

    assert response1.status_code == 200
    assert response1.json()["action"] == "ask_panel"

    # Message 2: Select ISP panel
    response2 = client.post(
        "/api/v1/ai/respond",
        json={
            "session_id": session_id,
            "message": "Jazz",
        },
    )

    assert response2.status_code == 200
    assert response2.json()["action"] == "ask_account"

    # Message 3: Provide fictional account number
    response3 = client.post(
        "/api/v1/ai/respond",
        json={
            "session_id": session_id,
            "message": "ISP001",
        },
    )

    assert response3.status_code == 200
    assert response3.json()["action"] == "verification_required"

    # Confirm selected panel is remembered
    assert panel_sessions[session_id]["panel"] == "jazz"
    assert panel_sessions[session_id]["account_number"] == "ISP001"

    # Clean up after test
    panel_sessions.pop(session_id, None)
