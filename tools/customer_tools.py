from langchain_core.tools import tool
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


@tool
def get_customer_status(customer_id: str) -> dict:
    """Look up the connection status of a fictional ISP customer."""

    customer = customers.get(customer_id)

    if customer is None:
        return {"error": "Customer not found"}

    return {
        "customer_id": customer_id,
        "connection_status": customer["status"]
    }

@tool
def get_customer_package(customer_id: str) -> dict:
    """Get the internet package of a fictional ISP customer."""

    customer = customers.get(customer_id)

    if customer is None:
        return {"error": "Customer not found"}

    return {
        "customer_id": customer_id,
        "package": customer["package"]
    }