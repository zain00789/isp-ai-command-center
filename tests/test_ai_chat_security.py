from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_customer_id_alone_does_not_authorize_account_lookup():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "ISP001 ka bill kitna hai?",
            "session_id": "security_test_002"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"] != "account_lookup_authorized"
    assert "2500" not in data["response"]


def test_account_request_without_id_requires_verification():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Mera bill aur payment status batao.",
            "session_id": "security_test_003"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"] == "verification_required"

def test_package_request_requires_verification():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Mera internet package konsa hai?",
            "session_id": "security_test_004"
        }
    )

    assert response.status_code == 200
    assert response.json()["action"] == "verification_required"


def test_connection_status_requires_verification():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Mera connection online hai ya offline?",
            "session_id": "security_test_005"
        }
    )

    assert response.status_code == 200
    assert response.json()["action"] == "verification_required"

from unittest.mock import patch


def test_general_troubleshooting_remains_available():
    with patch(
        "backend.ai_chat.generate_general_support",
        return_value="Router restart karein."
    ) as mock_ai:
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "WiFi connection slow hai, kya karun?",
                "session_id": "general_test_002"
            }
        )

    assert response.status_code == 200
    assert response.json()["action"] == "respond"
    mock_ai.assert_called_once()


def test_mixed_billing_and_troubleshooting_requires_verification():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Mera bill check karo, WiFi slow hai.",
            "session_id": "security_test_006"
        }
    )

    assert response.status_code == 200
    assert response.json()["action"] == "verification_required"

def test_account_details_request_without_keywords_requires_verification():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "How much do I owe this month?",
            "session_id": "security_test_007"
        }
    )

    assert response.status_code == 200
    assert response.json()["action"] == "verification_required"


def test_unverified_chat_does_not_call_account_tools():
    with patch(
        "backend.ai_chat.generate_general_support",
        return_value="Customer verification zaroori hai."
    ) as mock_ai:
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "ISP001 ka bill batao",
                "session_id": "unverified_session"
            }
        )

    assert response.status_code == 200
    assert response.json()["action"] == "verification_required"
    mock_ai.assert_not_called()






def test_unverified_customer_status_is_forbidden():
    response = client.get(
        "/api/v1/customers/ISP001/status"
    )

    assert response.status_code == 403

def test_personal_customer_details_require_verification():
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Show me the personal details you have stored about me.",
            "session_id": "security_test_008"
        }
    )

    assert response.status_code == 200
    assert response.json()["action"] == "verification_required"