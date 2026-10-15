
import re

from fastapi import APIRouter
from pydantic import BaseModel

from backend.general_support import generate_general_support


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/chat")
def chat_with_ai(request: ChatRequest):
    message = request.message.strip()

    # Allow common general troubleshooting questions.
    if (
        re.search(r"\b(slow|restart|speed|wifi|wi-fi)\b", message, re.IGNORECASE)
        and not re.search(
            r"\b(mera|meri|mere|my|ISP\d{3,}|bill|payment|package|plan|subscription|account|online|offline|status)\b",
            message,
            re.IGNORECASE
        )
    ):
        return {
            "intent": "general_support",
            "response": generate_general_support(message),
            "action": "respond"
        }

    # Temporary safety restriction:
    # Block customer IDs and common account/billing requests.
    if (
        re.search(r"\bISP\d{3,}\b", message, re.IGNORECASE)
        or re.search(
           r"\b(bill|billing|payment|invoice|due date|expiry|balance|package|plan|subscription|connection|online|offline|status|owe|owed|outstanding|personal|private|stored|profile)\b",
            message,
            re.IGNORECASE
        )
    ):
        return {
            "intent": "account_support",
            "response": (
                "Account details check karne ke liye "
                "customer verification zaroori hai."
            ),
            "action": "verification_required"
        }

    # General support only: no account tools attached.
    answer = generate_general_support(message)

    return {
        "intent": "general_support",
        "response": answer,
        "action": "respond"
    }
