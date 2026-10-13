
import re


# Fictional customer IDs used during development
TEST_CUSTOMER_IDS = {"ISP001", "ISP002"}


def extract_customer_id(text: str) -> str | None:
    """
    Find an explicitly supplied fictional customer ID.
    Never ask the LLM to invent an identifier.
    """
    match = re.search(
        r"\bISP\d{3,}\b",
        text,
        flags=re.IGNORECASE
    )

    if match:
        return match.group(0).upper()

    return None


def check_customer_id(text: str) -> dict:
    """
    Check whether the user supplied a known test ID.
    This is NOT identity authentication.
    """
    customer_id = extract_customer_id(text)

    if customer_id is None:
        return {
            "allowed": False,
            "customer_id": None,
            "reason": "missing_customer_id"
        }

    if customer_id not in TEST_CUSTOMER_IDS:
        return {
            "allowed": False,
            "customer_id": customer_id,
            "reason": "unknown_customer_id"
        }

    return {
        "allowed": True,
        "customer_id": customer_id,
        "reason": "test_id_found"
    }


if __name__ == "__main__":
    examples = [
        "Mera internet slow hai",
        "Mera customer ID ISP001 hai",
        "ISP999 ka bill bata dein"
    ]

    for example in examples:
        print(example, "->", check_customer_id(example))
