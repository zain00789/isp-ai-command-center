
import re


def detect_priority_intent(message: str) -> str | None:
    """
    Detect explicit customer requests using English
    and Roman Urdu phrases.

    This function only identifies intent.
    It does not access accounts or execute actions.
    """

    if not message or not message.strip():
        return None

    # Normalize case, punctuation and whitespace.
    text = message.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = " ".join(text.split())

    cancel_phrases = [
        "cancel complaint",
        "complaint cancel",
        "ticket cancel",
        "shikayat cancel",
        "complaint band kar",
        "shikayat band kar",
    ]

    ticket_status_phrases = [
        "complaint status",
        "complaint ka status",
        "complaint ki status",
        "ticket status",
        "ticket ka status",
        "shikayat ka status",
        "shikayat ki status",
        "shikayat ki update",
        "complaint ki update",
        "complaint number ka kya bana",
        "complaint ka kya bana",
        "ticket ka kya bana",
    ]

    complaint_phrases = [
        "complaint register",
        "register complaint",
        "complaint file",
        "complaint lodge",
        "complaint kar",
        "complaint likh",
        "shikayat darj",
        "shikayat register",
        "nayi shikayat likhwa",
        "shikayat likhwa",
        "complaint karwani",
    ]

    billing_phrases = [
        "mera bill",
        "bill kitna",
        "bill amount",
        "billing detail",
        "payment status",
        "apna bill check",
        "bill check karna",
        "bill dekhna",
        "bill bata",
    ]

    # Priority order matters.
    # Cancellation must not be mistaken for registration.

    if any(phrase in text for phrase in cancel_phrases):
        return "cancel_complaint"

    if any(phrase in text for phrase in ticket_status_phrases):
        return "ticket_status"

    if any(phrase in text for phrase in complaint_phrases):
        return "new_complaint"

    if any(phrase in text for phrase in billing_phrases):
        return "billing"

    return None


if __name__ == "__main__":
    examples = [
        "Meri shikayat ki update dein",
        "Complaint number ka kya bana?",
        "Mujhe apna bill check karna hai",
        "Meri complaint band kar dein",
        "Nayi shikayat likhwaani hai",
    ]

    for example in examples:
        print(
            example,
            "->",
            detect_priority_intent(example)
        )
