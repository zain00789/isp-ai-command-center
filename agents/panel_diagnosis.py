
from tools.panel_adapter import get_mock_account
from agents.diagnostic_agent import diagnose_connection


def analyze_panel_account(
    panel: str,
    account_number: str
) -> dict:
    """
    Combine a fictional panel lookup with diagnosis.

    For local testing only.
    Do not expose this function directly to unverified callers.
    """

    # Step 1: Retrieve fictional account information
    account = get_mock_account(
        panel=panel,
        account_number=account_number
    )

    # Step 2: Handle errors
    if "error" in account:
        return {
            "panel": panel,
            "account_number": account_number,
            "diagnosis": account["error"],
            "response": (
                "Account information nahi mil saki. "
                "Barah-e-karam details check karein."
            )
        }

    # Step 3: Analyze account data
    diagnosis = diagnose_connection(account)

    # Step 4: Return structured result
    return {
        "panel": account["panel"],
        "account_number": account["account_number"],
        "connection_status": account["connection_status"],
        "package_status": account["package_status"],
        "diagnosis": diagnosis["diagnosis"],
        "response": diagnosis["response"]
    }


if __name__ == "__main__":
    for panel in ["falcon", "jazz", "connect"]:
        result = analyze_panel_account(
            panel=panel,
            account_number="ISP001"
        )

        print("\nPanel:", panel)
        print("Diagnosis:", result["diagnosis"])
        print("AI:", result["response"])
