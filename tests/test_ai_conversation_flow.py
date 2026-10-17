
from unittest.mock import patch

import pytest

from backend.ai_chat import ChatRequest, chat_with_ai, conversation_history


@pytest.fixture(autouse=True)
def clear_chat_history():
    """Keep tests independent from each other."""
    conversation_history.clear()
    yield
    conversation_history.clear()


@pytest.mark.parametrize(
    "message",
    [
        "Mera internet slow hai",
        "Wi-Fi signal full hain",
        "Laptop par internet theek chal raha hai",
        "Mobile restart kar liya, phir bhi slow hai",
        "Wi-Fi forget karke reconnect kar liya",
        "Speed test mein 2 Mbps aa rahi hai",
        "Background apps sab band hain",
        "Router restart kar liya, phir bhi slow hai",
    ],
)
def test_general_troubleshooting_is_allowed(message):
    """Ordinary troubleshooting must reach the support AI."""
    with patch(
        "backend.ai_chat.generate_general_support",
        return_value="Aap ek aur check kar sakte hain.",
    ) as mock_ai:
        result = chat_with_ai(
            ChatRequest(
                session_id="troubleshooting-test",
                message=message,
            )
        )

    assert result["action"] == "respond"
    assert result["intent"] == "general_support"
    mock_ai.assert_called_once()


def test_mobile_wifi_clarification():
    """A mobile phone must not automatically mean mobile data."""
    with patch(
        "backend.ai_chat.generate_general_support"
    ) as mock_ai:
        result = chat_with_ai(
            ChatRequest(
                session_id="mobile-test",
                message="Sirf mobile par slow hai",
            )
        )

    assert result["action"] == "respond"
    assert "Wi-Fi" in result["response"]
    assert "mobile data" in result["response"]
    mock_ai.assert_not_called()


def test_conversation_history_is_passed_to_ai():
    """The next reply must receive earlier conversation turns."""
    with patch(
        "backend.ai_chat.generate_general_support",
        side_effect=[
            "Wi-Fi use kar rahe hain ya mobile data?",
            "Aap router ke paas hain?",
        ],
    ) as mock_ai:
        chat_with_ai(
            ChatRequest(
                session_id="history-test",
                message="Internet slow hai",
            )
        )

        chat_with_ai(
            ChatRequest(
                session_id="history-test",
                message="Wi-Fi use kar raha hoon",
            )
        )

    history = mock_ai.call_args.kwargs["history"]

    assert any(
        turn["content"] == "Internet slow hai"
        for turn in history
    )
    assert any(
        turn["content"] == "Wi-Fi use kar rahe hain ya mobile data?"
        for turn in history
    )


@pytest.mark.parametrize(
    "message",
    [
        "Mera bill kitna hai?",
        "Mere account ka status batao",
        "Mera payment check karo",
        "Mera package kya hai?",
        "ISP001 ka balance batao",
        "Mujhe batao mere kitne paise pending hain",
    ],
)
def test_account_requests_require_verification(message):
    """Account-specific requests must be blocked before the LLM."""
    with patch(
        "backend.ai_chat.generate_general_support"
    ) as mock_ai:
        result = chat_with_ai(
            ChatRequest(
                session_id="security-test",
                message=message,
            )
        )

    assert result["action"] == "verification_required"
    mock_ai.assert_not_called()
