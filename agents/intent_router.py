import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from llm_config import get_llm
load_dotenv()


class CustomerIntent(BaseModel):
    intent: Literal[
        "general_support",
        "billing",
        "new_complaint",
        "ticket_status",
        "cancel_complaint",
        "unclear",
    ] = Field(
        description="The customer's primary intention."
    )


llm = get_llm()
classifier = llm.with_structured_output(
    CustomerIntent
)


def detect_intent(message: str) -> str:
    result = classifier.invoke(
        [
            (
                "system",
                """Classify the customer's ISP support message.
Messages may be English, Urdu, or Roman Urdu.

new_complaint: Customer explicitly wants to register a new complaint.
ticket_status: Customer asks about an existing complaint.
cancel_complaint: Customer wants to cancel an existing complaint.
billing: Customer asks about bills or payments.
general_support: Internet problems, troubleshooting, packages,
connection status, greetings and other support questions.
unclear: Intention cannot be determined.

Only classify the request. Never perform any action."""
            ),
            ("human", message),
        ]
    )

    if result is None:
        return "unclear"

    return result.intent


if __name__ == "__main__":
    examples = [
        "Meri complaint register kar dein",
        "Meri complaint ka status kya hai?",
        "Mera internet slow hai",
        "ISP001 ka bill bata dein",
        "Meri complaint cancel kar dein",
    ]

    for message in examples:
        try:
            intent = detect_intent(message)
            print(f"{message} -> {intent}")
        except Exception as error:
            print(
                f"{message} -> ERROR: {type(error).__name__}"
            )