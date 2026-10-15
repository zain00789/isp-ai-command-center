
from langchain_core.tools import tool

from backend.authorization import is_customer_authorized


# Fictional customer billing records
bills = {
    "ISP001": {
        "amount": 2500,
        "currency": "PKR",
        "payment_status": "unpaid",
        "due_date": "2026-11-15"
    },
    "ISP002": {
        "amount": 4000,
        "currency": "PKR",
        "payment_status": "paid",
        "due_date": "2026-12-01"
    }
}


@tool
def get_customer_bill(customer_id: str) -> dict:
    """Get customer billing details only after authorization."""

    # No trusted authenticated session is available.
    # Deny access until backend verification exists.
    if not is_customer_authorized(
        customer_id=customer_id,
        session_id=""
    ):
        return {
            "error": "authorization_required",
            "message": (
                "Customer verification is required "
                "before accessing account information."
            )
        }

    bill = bills.get(customer_id)

    if bill is None:
        return {"error": "Customer bill not found"}

    return {
        "customer_id": customer_id,
        "amount": bill["amount"],
        "currency": bill["currency"],
        "payment_status": bill["payment_status"],
        "due_date": bill["due_date"]
    }
