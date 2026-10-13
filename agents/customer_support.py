import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage
)

from tools.customer_tools import get_customer_status

# Step 1: Load Gemini API settings
load_dotenv()

# Step 2: Connect to Gemini
llm = ChatGoogleGenerativeAI(
    model=os.environ["GEMINI_MODEL"],
    google_api_key=os.environ["GEMINI_API_KEY"]
)

# Step 3: Give Gemini access to our customer lookup tool
llm_with_tools = llm.bind_tools([get_customer_status])


# Function to display only text from Gemini's response
def extract_text(response):
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))

        return "\n".join(text_parts)

    return ""


# Step 4: Define the conversation
messages = [
    SystemMessage(content="""
    You are a polite ISP customer support assistant
    for an internet service provider in Pakistan.

    LANGUAGE RULES:
    - Reply in simple Roman Urdu using English letters.
    - Always address the customer as 'aap'.
    - Never use rude or informal language.
    - Keep your replies short and helpful.

    CUSTOMER SUPPORT RULES:
    - When asked about connection status, use get_customer_status.
    - Never invent customer information.
    - Only report connection status returned by the tool.
    - If the customer is offline, explain politely.
    - Ask one relevant troubleshooting question.
    - Never claim you accessed the real Falcon dashboard.

    This is a development environment using fictional customer data.
    """),

    HumanMessage(
        content="Check internet connection status for ISP001."
    )
]


# Step 5: Ask Gemini to decide whether a tool is needed
response = llm_with_tools.invoke(messages)

print("\nAI requested tools:", response.tool_calls)


# Step 6: Execute the requested customer lookup tool
messages.append(response)

for tool_call in response.tool_calls:

    if tool_call["name"] == "get_customer_status":

        result = get_customer_status.invoke(
            tool_call["args"]
        )

        print("\nTool result:", result)

        messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )


# Step 7: Generate the final customer response
if response.tool_calls:

    final_response = llm_with_tools.invoke(messages)

    print("\nAI Agent:")
    print(extract_text(final_response))

else:

    print("\nAI Agent:")
    print(extract_text(response))