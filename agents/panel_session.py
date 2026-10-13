
from tools.panel_router import select_panel


# Temporary memory for fictional voice sessions
panel_sessions = {}


def handle_panel_conversation(message: str, session_id: str) -> dict:
    """
    Collect panel and account number across multiple messages.

    Does not access real customer accounts.
    """

    if not session_id or not session_id.strip():
        return {
            "stage": "error",
            "response": "Session ID zaroori hai."
        }

    if not message or not message.strip():
        return {
            "stage": "clarify",
            "response": "Barah-e-karam apni baat dobara batayein."
        }

    session = panel_sessions.setdefault(
        session_id,
        {
            "stage": "ask_panel",
            "panel": None,
            "account_number": None
        }
    )

    stage = session["stage"]

    if stage == "ask_panel":
        selection = select_panel(message)

        if not selection["valid"]:
            return {
                "stage": "ask_panel",
                "response": (
                    "Aapka connection Jazz, Falcon ya Connect "
                    "mein se kis panel par registered hai?"
                )
            }

        session["panel"] = selection["panel"]
        session["stage"] = "ask_account"

        return {
            "stage": "ask_account",
            "panel": session["panel"],
            "response": (
                f"Shukriya. Aap ne {session['panel'].title()} "
                "panel select kiya hai. "
                "Ab apna registered account number batayein."
            )
        }

    if stage == "ask_account":
        account_number = message.strip()

        if len(account_number) < 3 or len(account_number) > 50:
            return {
                "stage": "ask_account",
                "response": "Barah-e-karam sahi account number batayein."
            }

        session["account_number"] = account_number
        session["stage"] = "verification_required"

        return {
            "stage": "verification_required",
            "panel": session["panel"],
            "account_number": account_number,
            "response": (
                "Aapki account details mil gayi hain. "
                "Account check karne se pehle "
                "verification zaroori hai."
            )
        }

    return {
        "stage": session["stage"],
        "panel": session["panel"],
        "response": (
            "Aapki details receive ho gayi hain. "
            "Verification abhi complete nahi hui."
        )
    }


if __name__ == "__main__":
    session_id = "voice-test-001"

    for message in [
        "Mera internet nahi chal raha",
        "Falcon",
        "ISP001"
    ]:
        result = handle_panel_conversation(message, session_id)
        print(result)
