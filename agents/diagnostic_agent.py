
from datetime import date


def diagnose_connection(account: dict) -> dict:
    """
    Diagnose a fictional ISP account from structured
    panel data. No live panel access or LLM needed.

    Dates must use YYYY-MM-DD format.
    """

    panel = account.get("panel")
    status = account.get("connection_status")
    package_status = account.get("package_status")
    expiry = account.get("expiry_date")

    if panel not in {"jazz", "falcon", "connect"}:
        return {
            "diagnosis": "unknown_panel",
            "response": "Panel ki information durust nahi hai."
        }

    if package_status == "expired":
        return {
            "diagnosis": "package_expired",
            "response": (
                "Aapka internet package expire ho chuka hai. "
                "Barah-e-karam renewal ke liye billing team "
                "se rabta karein."
            )
        }

    if package_status == "suspended":
        return {
            "diagnosis": "account_suspended",
            "response": (
                "Aapka account suspended show ho raha hai. "
                "Mazeed tafseel ke liye support team se "
                "rabta karein."
            )
        }

    if status == "offline":
        return {
            "diagnosis": "connection_offline",
            "response": (
                "Aapka package active hai lekin connection "
                "offline show ho raha hai. Router restart "
                "karke cables check karein. Agar masla "
                "barqarar rahe to technical team se rabta karein."
            )
        }

    if status == "online":
        return {
            "diagnosis": "connection_online",
            "response": (
                "Panel ke mutabiq aapka connection online hai. "
                "Barah-e-karam apne device aur Wi-Fi connection "
                "ko check karein."
            )
        }

    return {
        "diagnosis": "unknown",
        "response": (
            "Connection ki wajah abhi clear nahi hai. "
            "Support team ko mazeed checking karni hogi."
        )
    }


if __name__ == "__main__":

    test_accounts = [
        {
            "panel": "falcon",
            "connection_status": "offline",
            "package_status": "expired",
            "expiry_date": "2026-10-10"
        },
        {
            "panel": "jazz",
            "connection_status": "offline",
            "package_status": "active",
            "expiry_date": "2026-11-20"
        },
        {
            "panel": "connect",
            "connection_status": "online",
            "package_status": "active",
            "expiry_date": "2026-11-25"
        }
    ]

    for account in test_accounts:
        result = diagnose_connection(account)

        print("\nPanel:", account["panel"])
        print("Diagnosis:", result["diagnosis"])
        print("AI:", result["response"])
