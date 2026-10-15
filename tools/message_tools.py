
from langchain_core.tools import tool

from backend.authorization import is_customer_authorized


# Temporary storage for simulated messages
sent_messages = []


@tool
def send_test_message(
    customer_id: str,
    ticket_id: str
) -> dict:
    """
    Queue a fictional complaint confirmation message.

    Secure customer authorization is required.
    No real SMS or WhatsApp messages are sent.
    """

    # Temporary deny-by-default protection.
    # A customer ID or ticket ID does not prove identity.
    if not is_customer_authorized(
        customer_id=customer_id,
        session_id=""
    ):
        return {
            "error": "authorization_required",
            "message": (
                "Secure customer verification is required "
                "before sending a complaint notification."
            )
        }

    message = (
        "Assalam-o-Alaikum! "
        "Aapki internet complaint register ho gayi hai. "
        f"Aapka ticket number {ticket_id} hai."
    )

    record = {
        "customer_id": customer_id,
        "ticket_id": ticket_id,
        "channel": "simulation",
        "message": message,
        "status": "simulated"
    }

    sent_messages.append(record)

    return record
