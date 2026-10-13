from langchain_core.tools import tool

# Fictional tickets stored temporarily in memory
tickets = []

@tool
def create_support_ticket(
    customer_id: str,
    issue: str
) -> dict:
    """Create a fictional ISP support ticket for testing."""

    ticket_id = f"TKT-{len(tickets) + 1:04d}"

    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "issue": issue,
        "status": "open"
    }

    tickets.append(ticket)

    return ticket