
from langchain_core.messages import SystemMessage, HumanMessage

from agents.intent_router import detect_intent
from agents.support_graph import app
from tools.customer_guard import check_customer_id
from agents.panel_session import handle_panel_conversation, panel_sessions
SYSTEM_PROMPT = """
You are a polite Pakistani ISP customer support assistant.

Always respond in simple Roman Urdu.
Address customers respectfully using 'aap'.

You can help with:
- Internet troubleshooting
- Internet connection status
- Internet packages
- Billing questions

Use tools when customer information is needed.
Never invent customer information or customer IDs.

All customer data is fictional for testing.
Never claim to access the real Falcon Broadband system.

Do not create tickets directly.
Complaint registration requires a separate
verified and explicitly confirmed workflow.
IMPORTANT SAFETY RULES:
- Never invent customer IDs, phone numbers, helpline numbers,
  office addresses, service hours, or technician appointments.
- Never claim that a technician has been scheduled unless
  an authorized backend tool confirms the appointment.
- If a customer ID is missing, ask the customer to provide it.
- Never guess a customer ID or call account lookup tools
  using invented identifiers.
- Use only verified tool results for account information.
- If the ISP's helpline is unknown, simply say:
  "Aap hamari support team se rabta kar sakte hain."
- Reply in Roman Urdu using English letters only.
"""


# Temporary in-memory conversation history
conversations = {}


def extract_text(message):
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
    Process customer text and return structured output
    for a future voice system or FastAPI backend.
    """

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

    # Start a new panel conversation
    if message.strip().lower() == "start connection check":
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

    # Continue an existing panel conversation
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
   
    # Step 1: Retrieve previous conversation
    history = conversations.get(session_id, [])

    # Step 2: Prepare relevant conversation context
    previous_messages = []

    for item in history[-6:]:
        if isinstance(item, HumanMessage):
            previous_messages.append(
                f"Customer: {item.content}"
            )
        elif isinstance(item, SystemMessage):
            continue
        else:
            if hasattr(item, "content"):
                text = extract_text(item)
                if text:
                    previous_messages.append(f"AI: {text}")

    context = "\n".join(previous_messages)

    if context:
        intent_message = (
            f"Previous conversation:\n{context}\n\n"
            f"Latest customer message:\n{message}"
        )
    else:
        intent_message = message

    # Step 3: Classify customer intention
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

    # Start panel selection for internet connection problems
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

    if any(
        keyword in message.lower()
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
    # Step 4: Handle different intentions
    if intent == "new_complaint":
        return {
            "intent": intent,
            "response": (
                "Aapki complaint register karne ke liye "
                "verification aur confirmation zaroori hai."
            ),
            "action": "start_complaint"
        }

    if intent == "ticket_status":
        return {
            "intent": intent,
            "response": (
                "Complaint status checking filhal "
                "available nahi hai."
            ),
            "action": "ticket_status_unavailable"
        }

    if intent == "cancel_complaint":
        return {
            "intent": intent,
            "response": (
                "Complaint cancellation filhal "
                "available nahi hai."
            ),
            "action": "cancellation_unavailable"
        }

    if intent == "unclear":
        # Continue an existing support conversation when the
        # latest message is a short reply to the agent.
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

    # Check for an explicitly supplied fictional customer ID
    guard = check_customer_id(message)

    if guard["reason"] == "unknown_customer_id":
        return {
            "intent": intent,
            "response": (
                "Yeh customer ID hamare test records mein nahi mila. "
                "Barah-e-karam ID dobara check karein."
            ),
            "action": "invalid_customer_id"
        }

    if guard["reason"] == "missing_customer_id":
        # Allow general troubleshooting without an account lookup.
        # This is only a preliminary check, not tool-level enforcement.
        print("No new customer ID supplied in this message.")

    # Step 5: Continue the support conversation
    if not history:
        history = [SystemMessage(content=SYSTEM_PROMPT)]

    candidate_messages = history + [
        HumanMessage(content=message)
    ]

    try:
        result = app.invoke(
            {"messages": candidate_messages},
            config={"recursion_limit": 10}
        )

        answer = extract_text(result["messages"][-1])

        if not answer:
            return {
                "intent": intent,
                "response": (
                    "Maazrat, jawab samajh nahi aaya. "
                    "Barah-e-karam dobara batayein."
                ),
                "action": "clarify"
            }

        # Save successful conversation
        conversations[session_id] = result["messages"]

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
