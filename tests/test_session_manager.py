
from unittest.mock import patch

from langchain_core.messages import HumanMessage

from agents.session_manager import (
    check_session,
    clear_session,
    session_last_activity,
)
from agents.panel_session import panel_sessions


def test_new_session():
    conversations = {}
    session_id = "test-new-session"

    clear_session(session_id, conversations)

    with patch("agents.session_manager.time.monotonic", return_value=1000):
        expired = check_session(session_id, conversations)

    assert expired is False
    assert session_last_activity[session_id] == 1000

    clear_session(session_id, conversations)


def test_active_session():
    conversations = {
        "test-active-session": [
            HumanMessage(content="Mera Wi-Fi slow hai")
        ]
    }

    session_id = "test-active-session"

    clear_session(session_id, {})
    session_last_activity[session_id] = 1000

    with patch("agents.session_manager.time.monotonic", return_value=1500):
        expired = check_session(session_id, conversations)

    assert expired is False
    assert session_id in conversations

    clear_session(session_id, conversations)


def test_expired_session():
    session_id = "test-expired-session"

    conversations = {
        session_id: [
            HumanMessage(content="Mera internet slow hai")
        ]
    }

    panel_sessions[session_id] = {
        "stage": "ask_account",
        "panel": "jazz"
    }

    session_last_activity[session_id] = 1000

    # Simulate 31 minutes passing.
    with patch("agents.session_manager.time.monotonic", return_value=2860):
        expired = check_session(session_id, conversations)

    assert expired is True
    assert session_id not in conversations
    assert session_id not in panel_sessions
    assert session_last_activity[session_id] == 2860

    clear_session(session_id, conversations)


def test_clear_session():
    session_id = "test-clear-session"

    conversations = {
        session_id: [
            HumanMessage(content="Hello")
        ]
    }

    panel_sessions[session_id] = {
        "stage": "ask_panel"
    }

    session_last_activity[session_id] = 1000

    clear_session(session_id, conversations)

    assert session_id not in conversations
    assert session_id not in panel_sessions
    assert session_id not in session_last_activity
