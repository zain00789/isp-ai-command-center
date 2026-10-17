
import re

from fastapi import APIRouter
from pydantic import BaseModel

from backend.general_support import generate_general_support
from backend.conversation_store import save_conversation_message


router = APIRouter()

# Temporary in-memory history for AI context.
# SQLite stores the conversation permanently.
conversation_history = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/chat")
def chat_with_ai(request: ChatRequest):
    message = request.message.strip()
    session_id = request.session_id.strip()

    if not message:
        return {
            "intent": "invalid_request",
            "response": "Please apna message likhein.",
            "action": "respond",
        }

    if not session_id:
        return {
            "intent": "invalid_request",
            "response": "Session ID required hai.",
            "action": "respond",
        }

    # Temporary account security guard.
    # Session ID is NOT proof of customer verification.
    if (
        re.search(r"\bISP\d{3,}\b", message, re.IGNORECASE)
        or re.search(
            r"\b("
            r"bill|billing|payment|invoice|due date|expiry|balance|"
            r"package|plan|subscription|online|offline|status|"
            r"owe|owed|outstanding|personal|private|stored|profile|account|"
            r"paise|paisa|pending|raqam"
            r")\b",
            message,
            re.IGNORECASE,
        )
    ):
        answer = (
            "Account details check karne ke liye "
            "customer verification zaroori hai."
        )

        # Store the discussion without exposing account details.
        save_conversation_message(session_id, "customer", message)
        save_conversation_message(session_id, "assistant", answer)

        return {
            "intent": "account_support",
            "response": answer,
            "action": "verification_required",
        }

    # Create in-memory history for a new session.
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    # Persist customer's message in SQLite.
    save_conversation_message(session_id, "customer", message)

    # Add customer message to AI context.
    conversation_history[session_id].append({
        "role": "user",
        "content": message,
    })

    # Clarify ambiguous mobile-phone replies.
    if re.search(
        r"\b(sirf mobile|only mobile)\b",
        message,
        re.IGNORECASE,
    ):
        answer = (
            "Aap mobile par Wi-Fi use kar rahe hain "
            "ya mobile data?"
        )

    else:
        # Generate troubleshooting response using session history.
        answer = generate_general_support(
            message,
            history=conversation_history[session_id][:-1],
        )

    # Add AI reply to in-memory history.
    conversation_history[session_id].append({
        "role": "assistant",
        "content": answer,
    })

    # Persist AI reply in SQLite.
    save_conversation_message(session_id, "assistant", answer)

    return {
        "intent": "general_support",
        "response": answer,
        "action": "respond",
    }
