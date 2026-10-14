
from tools.panel_adapter import get_mock_account
from agents.diagnostic_agent import diagnose_connection


def analyze_panel_account(
    panel: str,
    account_number: str
) -> dict:
    """
    Analyze fictional ISP account information.

    Account access requires backend authorization.
    Unverified requests must not receive account details.
    """

    # Step 1: Request account information
    account = get_mock_account(
        panel=panel,
        account_number=account_number
    )

    # Step 2: Block unauthorized requests
    if account.get("error") == "authorization_required":
        return {
            "diagnosis": "authorization_required",
            "response": (
                "Aapke account ki details check karne ke liye "
                "secure verification zaroori hai."
            )
        }

    # Step 3: Handle other lookup errors
    if "error" in account:
        return {
            "diagnosis": "account_lookup_unavailable",
            "response": (
                "Account information filhal available nahi hai. "
                "Barah-e-karam support team se rabta karein."
            )
        }

    # Step 4: Diagnose authorized account data
    diagnosis = diagnose_connection(account)

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
