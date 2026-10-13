from langchain_core.tools import tool

# Fictional customers for testing
test_customers = {
    "ISP001": {
        "phone": "03000000001"
    },
    "ISP002": {
        "phone": "03000000002"
    }
}


@tool
def check_customer_record(
    customer_id: str,
    phone: str
) -> dict:
    """Check whether fictional customer details match."""

    customer = test_customers.get(customer_id)

    if customer is None:
        return {
            "match": False,
            "message": "Customer not found"
        }

    if customer["phone"] != phone:
        return {
            "match": False,
            "message": "Customer details do not match"
        }

    return {
        "match": True,
        "message": "Fictional customer record matched"
    }