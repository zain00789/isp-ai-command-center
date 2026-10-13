from langchain_core.tools import tool

# Temporary storage for simulated messages
sent_messages = []


@tool
def send_test_message(
    customer_id: str,
    ticket_id: str
) -> dict:
    """Queue a fictional ISP complaint confirmation message."""

    message = (
        f"Assalam-o-Alaikum! "
        f"Aapki internet complaint register ho gayi hai. "
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