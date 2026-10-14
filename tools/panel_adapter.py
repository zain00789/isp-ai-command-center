
from backend.authorization import is_customer_authorized


# Fictional account records for local testing
MOCK_ACCOUNTS = {
    "falcon": {
        "ISP001": {
            "connection_status": "offline",
            "package_status": "expired",
            "expiry_date": "2026-10-10",
        }
    },
    "jazz": {
        "ISP001": {
            "connection_status": "offline",
            "package_status": "active",
            "expiry_date": "2026-11-20",
        }
    },
    "connect": {
        "ISP001": {
            "connection_status": "online",
            "package_status": "active",
            "expiry_date": "2026-11-25",
        }
    },
}


def get_mock_account(panel: str, account_number: str) -> dict:
    """
    Return fictional account details only after authorization.

    Temporary deny-by-default implementation.
    No live ISP panel access.
    """

    normalized_panel = panel.strip().lower()
    normalized_account = account_number.strip().upper()

    # Authorization must happen before account lookup.
    # The empty session ID does not grant access.
    if not is_customer_authorized(
        customer_id=normalized_account,
        session_id=""
    ):
        return {
            "error": "authorization_required",
            "message": (
                "Secure customer verification is required "
                "before accessing panel account information."
            )
        }

    if normalized_panel not in MOCK_ACCOUNTS:
        return {
            "error": "unknown_panel",
            "message": "Unsupported ISP panel."
        }

    account = MOCK_ACCOUNTS[normalized_panel].get(
        normalized_account
    )

    if account is None:
        return {
            "error": "account_not_found",
            "message": "Fictional account not found."
        }

    return {
        "panel": normalized_panel,
        "account_number": normalized_account,
        "connection_status": account["connection_status"],
        "package_status": account["package_status"],
        "expiry_date": account["expiry_date"],
    }


if __name__ == "__main__":
    for panel in ["falcon", "jazz", "connect"]:
        result = get_mock_account(panel, "ISP001")
        print("\nPanel:", panel)
        print(result)
