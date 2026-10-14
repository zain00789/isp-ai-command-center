
from langchain_core.tools import tool

from backend.authorization import is_customer_authorized


# Fictional tickets stored temporarily in memory
tickets = []


@tool
def create_support_ticket(
    customer_id: str,
    issue: str
) -> dict:
    """
    Create a fictional ISP support ticket.

    Trusted customer authorization is required.
    """

    # Temporary deny-by-default security check.
    # Never treat a customer ID as proof of identity.
    if not is_customer_authorized(
        customer_id=customer_id,
        session_id=""
    ):
        return {
            "error": "authorization_required",
            "message": (
                "Secure customer verification is required "
                "before creating a support ticket."
            )
        }

    # This section must only execute after authorization.
    ticket_id = f"TKT-{len(tickets) + 1:04d}"

    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "issue": issue,
        "status": "open"
    }

    tickets.append(ticket)

    return ticket
