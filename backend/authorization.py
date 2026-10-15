def is_customer_authorized(customer_id: str, session_id: str) -> bool:
    """
    Temporary security guard.

    Deny all customer account lookups until
    trusted backend authentication is implemented.
    """
    return False