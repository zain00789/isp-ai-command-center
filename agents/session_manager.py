
import time

from agents.panel_session import panel_sessions


SESSION_TIMEOUT_SECONDS = 30 * 60

# Store the last activity time for each session.
session_last_activity = {}


def check_session(session_id: str, conversations: dict) -> bool:
    """
    Check whether a session has expired.

    Returns True if the session expired.
    Returns False if it is new or still active.
    """

    now = time.monotonic()

    last_activity = session_last_activity.get(session_id)

    expired = (
        last_activity is not None
        and now - last_activity > SESSION_TIMEOUT_SECONDS
    )

    if expired:
        conversations.pop(session_id, None)
        panel_sessions.pop(session_id, None)

    session_last_activity[session_id] = now

    return expired


def clear_session(session_id: str, conversations: dict):
    """
    Clear a customer's temporary conversation state.
    """

    conversations.pop(session_id, None)
    panel_sessions.pop(session_id, None)
    session_last_activity.pop(session_id, None)
