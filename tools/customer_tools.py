
from langchain_core.tools import tool

from backend.authorization import is_customer_authorized


# Fictional customer data for development only
customers = {
    "ISP001": {
        "package": "20 Mbps",
        "status": "offline",
        "expiry": "2026-11-15"
    },
    "ISP002": {
        "package": "50 Mbps",
        "status": "online",
        "expiry": "2026-12-01"
    }
}


def authorization_denied() -> dict:
    return {
        "error": "authorization_required",
        "message": (
            "Customer verification is required "
            "before accessing account information."
        )
    }


@tool
def get_customer_status(customer_id: str) -> dict:
    """Check customer connection status only after authorization."""

    # No trusted authenticated session is available to this tool.
    # Never use a customer ID as proof of identity.
    # Keep authorization denied until backend verification exists.
    if not is_customer_authorized(
        customer_id=customer_id,
        session_id=""
    ):
        return authorization_denied()

    customer = customers.get(customer_id)

    if customer is None:
        return {"error": "Customer not found"}

    return {
        "customer_id": customer_id,
        "connection_status": customer["status"]
    }


@tool
def get_customer_package(customer_id: str) -> dict:
    """Check customer package only after authorization."""

    if not is_customer_authorized(
        customer_id=customer_id,
        session_id=""
    ):
        return authorization_denied()

    customer = customers.get(customer_id)

    if customer is None:
        return {"error": "Customer not found"}

    return {
        "customer_id": customer_id,
        "package": customer["package"]
    }
