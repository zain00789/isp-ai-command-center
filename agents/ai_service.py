
from langchain_core.messages import SystemMessage, HumanMessage

from agents.intent_router import detect_intent
from agents.intent_priority import detect_priority_intent
from agents.support_graph import app
from agents.panel_session import handle_panel_conversation, panel_sessions
from agents.session_manager import check_session, clear_session
from tools.customer_guard import check_customer_id


SYSTEM_PROMPT = """
You are a polite Pakistani ISP customer support assistant.

Always respond in simple Roman Urdu.
Address customers respectfully using 'aap'.

You can help with:
- Internet troubleshooting
- Internet connection status
- Internet packages
- Billing questions
- General ISP support

Never invent customer information or customer IDs.

All customer data is fictional for testing.
Never claim to access real ISP customer systems.

Do not create tickets directly.
Complaint registration requires a separate
verified and explicitly confirmed workflow.

IMPORTANT SAFETY RULES:
- Never invent customer IDs, phone numbers, helpline numbers,
  office addresses, service hours, or technician appointments.
- Never claim that a technician has been scheduled unless
  an authorized backend confirms the appointment.
- Never guess a customer ID.
- Use only verified backend results for account information.
- If the ISP's helpline is unknown, simply say:
  "Aap hamari support team se rabta kar sakte hain."
- Reply in Roman Urdu using English letters only.
- Do not recommend factory resetting an ISP router.
- Do not recommend firmware updates without ISP guidance.

ACCOUNT SECURITY RULES:
- Account lookup tools are currently disabled.
- Never claim to have checked a customer's account.
- Never reveal package, billing, or connection details
  for a specific account.
- An account number or phone number is not verification.
- Account-specific information requires secure verification
  through the backend.
"""


# Temporary in-memory conversation history
conversations = {}


def extract_text(message):
    """
    Extract text from an AI or customer message.
    """

    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

    return ""


def process_customer_message(message: str, session_id: str) -> dict:
    """
    Process customer messages and return structured
    responses for FastAPI or a future voice interface.
    """

    # --------------------------------------------------
    # STEP 1: Validate input
    # --------------------------------------------------

    if not message or not message.strip():
        return {
            "intent": "unclear",
            "response": "Barah-e-karam apna sawal batayein.",
            "action": "clarify"
        }

    if not session_id or not session_id.strip():
        return {
            "intent": "unclear",
            "response": "Session ID zaroori hai.",
            "action": "error"
        }

    normalized_message = " ".join(message.lower().split())

    # --------------------------------------------------
    # STEP 2: Manual session reset
    # --------------------------------------------------

    if normalized_message in {
        "new conversation",
        "new chat",
        "start over",
        "start fresh",
    }:
        clear_session(
            session_id=session_id,
            conversations=conversations
        )

        return {
            "intent": "session_reset",
            "response": (
                "Nayi conversation shuru ho gayi hai. "
                "Batayein, main aapki kya madad kar sakta hoon?"
            ),
            "action": "session_reset"
        }

    # --------------------------------------------------
    # STEP 3: Check session expiration
    # --------------------------------------------------

    check_session(
        session_id=session_id,
        conversations=conversations
    )

    # --------------------------------------------------
    # STEP 4: Explicitly start connection check
    # --------------------------------------------------

    if normalized_message == "start connection check":

        panel_sessions.pop(session_id, None)

        panel_result = handle_panel_conversation(
            message=message,
            session_id=session_id
        )

        return {
            "intent": "connection_issue",
            "response": panel_result["response"],
            "action": panel_result["stage"]
        }

    # --------------------------------------------------
    # STEP 5: Centralized priority intent detection
    # --------------------------------------------------

    priority_intent = detect_priority_intent(message)

    # Allow explicit requests to interrupt an active
    # ISP panel-selection conversation.

    if session_id in panel_sessions and priority_intent:

        panel_sessions.pop(session_id, None)

        if priority_intent == "new_complaint":
            return {
                "intent": "new_complaint",
                "response": (
                    "Aapki complaint register karne ke liye "
                    "secure customer verification aur "
                    "aapki confirmation zaroori hai. "
                    "Filhal complaint register nahi hui."
                ),
                "action": "start_complaint"
            }

        if priority_intent == "billing":
            return {
                "intent": "billing",
                "response": (
                    "Billing details dekhne ke liye "
                    "secure customer verification zaroori hai. "
                    "Filhal account details available nahi hain."
                ),
                "action": "verification_required"
            }

        if priority_intent == "ticket_status":
            return {
                "intent": "ticket_status",
                "response": (
                    "Complaint status checking filhal "
                    "available nahi hai. "
                    "Account-specific information ke liye "
                    "secure verification zaroori hai."
                ),
                "action": "ticket_status_unavailable"
            }

        if priority_intent == "cancel_complaint":
            return {
                "intent": "cancel_complaint",
                "response": (
                    "Complaint cancellation filhal "
                    "available nahi hai. "
                    "Koi complaint cancel nahi hui."
                ),
                "action": "cancellation_unavailable"
            }

    # --------------------------------------------------
    # STEP 6: Continue an existing panel conversation
    # --------------------------------------------------

    if session_id in panel_sessions:

        panel_result = handle_panel_conversation(
            message=message,
            session_id=session_id
        )

        return {
            "intent": "account_identification",
            "response": panel_result["response"],
            "action": panel_result["stage"]
        }

    # --------------------------------------------------
    # STEP 7: Load previous conversation history
    # --------------------------------------------------

    history = conversations.get(session_id, [])

    previous_messages = []

    for item in history[-6:]:

        if isinstance(item, HumanMessage):
            previous_messages.append(
                f"Customer: {item.content}"
            )

        elif isinstance(item, SystemMessage):
            continue

        elif hasattr(item, "content"):
            text = extract_text(item)

            if text:
                previous_messages.append(
                    f"AI: {text}"
                )

    context = "\n".join(previous_messages)

    if context:
        intent_message = (
            f"Previous conversation:\n{context}\n\n"
            f"Latest customer message:\n{message}"
        )
    else:
        intent_message = message

    # --------------------------------------------------
    # STEP 8: Detect intent using the AI classifier
    # --------------------------------------------------

    try:
        intent = detect_intent(intent_message)

    except Exception:
        return {
            "intent": "unclear",
            "response": (
                "AI service filhal available nahi hai. "
                "Dobara koshish karein."
            ),
            "action": "error"
        }

    # --------------------------------------------------
    # STEP 9: Handle complaint requests
    # --------------------------------------------------

    # Explicit requests take priority over ordinary
    # connection-problem keywords.

    if (
        priority_intent == "new_complaint"
        or intent == "new_complaint"
    ):
        return {
            "intent": "new_complaint",
            "response": (
                "Aapki complaint register karne ke liye "
                "secure customer verification aur "
                "aapki confirmation zaroori hai. "
                "Filhal complaint register nahi hui."
            ),
            "action": "start_complaint"
        }

    # --------------------------------------------------
    # STEP 10: Detect connection problems
    # --------------------------------------------------

    connection_keywords = [
        "internet nahi chal",
        "net nahi chal",
        "internet band",
        "net band",
        "internet slow",
        "net slow",
        "connection problem",
        "connection issue",
        "wifi nahi chal",
        "wifi band",
        "no internet",
        "internet not working"
    ]

    # Avoid starting a connection check when the
    # customer explicitly asked for another workflow.

    if not priority_intent and any(
        keyword in normalized_message
        for keyword in connection_keywords
    ):

        panel_sessions.pop(session_id, None)

        panel_result = handle_panel_conversation(
            message=message,
            session_id=session_id
        )

        return {
            "intent": "connection_issue",
            "response": panel_result["response"],
            "action": panel_result["stage"]
        }

    # --------------------------------------------------
    # STEP 11: Handle ticket status
    # --------------------------------------------------

    if (
        priority_intent == "ticket_status"
        or intent == "ticket_status"
    ):
        return {
            "intent": "ticket_status",
            "response": (
                "Complaint status checking filhal "
                "available nahi hai. "
                "Account-specific information ke liye "
                "secure verification zaroori hai."
            ),
            "action": "ticket_status_unavailable"
        }

    # --------------------------------------------------
    # STEP 12: Handle complaint cancellation
    # --------------------------------------------------

    if (
        priority_intent == "cancel_complaint"
        or intent == "cancel_complaint"
    ):
        return {
            "intent": "cancel_complaint",
            "response": (
                "Complaint cancellation filhal "
                "available nahi hai. "
                "Koi complaint cancel nahi hui."
            ),
            "action": "cancellation_unavailable"
        }

    # --------------------------------------------------
    # STEP 13: Handle billing safely
    # --------------------------------------------------

    if priority_intent == "billing":
        return {
            "intent": "billing",
            "response": (
                "Billing details dekhne ke liye "
                "secure customer verification zaroori hai. "
                "Filhal account details available nahi hain."
            ),
            "action": "verification_required"
        }

    # --------------------------------------------------
    # STEP 14: Handle unclear intent
    # --------------------------------------------------

    if intent == "unclear":

        if history:
            intent = "general_support"

        else:
            return {
                "intent": "unclear",
                "response": (
                    "Barah-e-karam apna sawal "
                    "thori wazahat se batayein."
                ),
                "action": "clarify"
            }

    # --------------------------------------------------
    # STEP 15: Handle fictional customer ID guard
    # --------------------------------------------------

    guard = check_customer_id(message)

    if guard["reason"] == "unknown_customer_id":
        return {
            "intent": intent,
            "response": (
                "Account-specific information ke liye "
                "secure verification zaroori hai."
            ),
            "action": "verification_required"
        }

    # No account lookup is performed in this flow.
    # A customer ID alone does not authorize access.

    # --------------------------------------------------
    # STEP 16: Continue LangGraph support conversation
    # --------------------------------------------------

    if not history:
        history = [
            SystemMessage(content=SYSTEM_PROMPT)
        ]

    candidate_messages = history + [
        HumanMessage(content=message)
    ]

    try:
        result = app.invoke(
            {"messages": candidate_messages},
            config={"recursion_limit": 10}
        )

        answer = extract_text(
            result["messages"][-1]
        )

        if not answer:
            return {
                "intent": intent,
                "response": (
                    "Maazrat, jawab samajh nahi aaya. "
                    "Barah-e-karam dobara batayein."
                ),
                "action": "clarify"
            }

        # --------------------------------------------------
        # STEP 17: Save limited conversation history
        # --------------------------------------------------

        all_messages = result["messages"]

        system_messages = [
            msg for msg in all_messages
            if isinstance(msg, SystemMessage)
        ]

        non_system_messages = [
            msg for msg in all_messages
            if not isinstance(msg, SystemMessage)
        ]

        conversations[session_id] = (
            system_messages[:1]
            + non_system_messages[-10:]
        )

        return {
            "intent": intent,
            "response": answer,
            "action": "respond"
        }

    except Exception:
        return {
            "intent": intent,
            "response": (
                "Maazrat, abhi jawab dene mein "
                "masla aa raha hai. Dobara koshish karein."
            ),
            "action": "error"
        }


if __name__ == "__main__":
    print("AI service is ready for testing.")
