from langchain_core.messages import HumanMessage, SystemMessage

from llm_config import get_llm


# This model has NO account lookup tools attached.
llm = get_llm()

SYSTEM_PROMPT = """
You are a polite Pakistani ISP support assistant.

Reply in simple Roman Urdu using English letters.

You can provide general internet troubleshooting advice.

You cannot access customer accounts, bills, packages,
connection status, or private customer information.

Never claim to have checked a customer account.
Never invent ISP package prices, speeds, or policies.

If account-specific information is requested, explain
that customer verification is required.
"""


def generate_general_support(message: str) -> str:
    result = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=message),
    ])

    return result.content