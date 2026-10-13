
from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from agents.support_graph import app
from agents.complaint_graph import app as complaint_app
from agents.intent_router import detect_intent


# Instructions for our ISP AI Agent
SYSTEM_PROMPT = """
You are a polite Pakistani ISP customer support assistant.

LANGUAGE RULES:
- Always reply in simple Roman Urdu using English letters.
- Address customers respectfully using 'aap'.
- Keep responses short, clear, and helpful.

YOUR RESPONSIBILITIES:
- Answer general internet service questions.
- Check fictional customer connection status.
- Check fictional customer internet packages.
- Check fictional customer billing information.
- Provide basic internet troubleshooting advice.

TOOL RULES:
- Use get_customer_status for connection status.
- Use get_customer_package for internet packages.
- Use get_customer_bill for billing questions.
- Never invent customer information.
- Never claim to access the live Falcon Broadband dashboard.
- All customer records are fictional test data.

COMPLAINT REGISTRATION:
- Complaint registration is handled by a separate workflow.
- Never claim that a complaint has been registered
  unless the application confirms ticket creation.
- Never invent ticket numbers or notification delivery.
"""


# Extract customer-facing text from Gemini
def extract_text(message):

    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "text"
            ):
                text_parts.append(block.get("text", ""))

        return "\n".join(text_parts)

    return ""


# Handle fictional complaint registration
def handle_complaint():

    print("\n--- ISP Complaint Registration ---")

    customer_id = input("Customer ID: ").strip()
    phone = input("Registered phone: ").strip()
    issue = input("Describe your problem: ").strip()

    # Check required information
    if not customer_id or not phone or not issue:
        print("\nMissing information. Complaint cancelled.\n")
        return

    # Display complaint before confirmation
    print("\nComplaint details:")
    print("Customer:", customer_id)
    print("Issue:", issue)

    answer = input(
        "Do you want to register this complaint? (yes/no): "
    ).strip().lower()

    # Explicit confirmation is required
    if answer != "yes":
        print("\nComplaint cancelled.\n")
        return

    # Execute existing complaint workflow
    try:
        result = complaint_app.invoke({
            "customer_id": customer_id,
            "phone": phone,
            "issue": issue,
            "confirmed": True,
            "matched": False,
            "result": "",
            "ticket_id": "",
            "message_status": ""
        })

        print("\nAI Agent:", result["result"])
        print("Message status:", result["message_status"])
        print()

    except Exception as error:
        print(
            "\nComplaint workflow failed:",
            type(error).__name__
        )
        print(
            "Please check the workflow before trying again.\n"
        )


# Main interactive chatbot
def main():

    print("\n====================================")
    print("     ISP AI CUSTOMER SUPPORT")
    print("====================================")
    print("Type 'exit' to close the chatbot.\n")

    # Keep conversation history during this session
    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]

    while True:

        # Receive customer question
        question = input("Customer: ").strip()

        # Exit chatbot
        if question.lower() == "exit":
            print("\nSession ended. Allah Hafiz!")
            break

        # Ignore empty messages
        if not question:
            continue

        # Step 1: Detect customer intent using Gemini
        try:
            intent = detect_intent(question)
            print("Detected intent:", intent)

        except Exception as error:
            print(
                "\nIntent detection failed:",
                type(error).__name__
            )
            print("Please try again.\n")
            continue

        # Step 2: Route new complaints
        if intent == "new_complaint":
            handle_complaint()
            continue

        # Step 3: Handle existing ticket status requests
        if intent == "ticket_status":
            print(
                "\nAI Agent: Existing complaint status "
                "checking abhi available nahi hai.\n"
            )
            continue

        # Step 4: Handle cancellation requests
        if intent == "cancel_complaint":
            print(
                "\nAI Agent: Existing complaint cancellation "
                "abhi available nahi hai.\n"
            )
            continue

        # Step 5: Handle unclear requests
        if intent == "unclear":
            print(
                "\nAI Agent: Barah-e-karam apni "
                "request thori wazahat se batayein.\n"
            )
            continue

        # Step 6: Normal support and billing questions
        new_message = HumanMessage(content=question)

        candidate_messages = messages + [new_message]

        try:

            # Execute LangGraph support workflow
            result = app.invoke(
                {"messages": candidate_messages},
                config={"recursion_limit": 10}
            )

            # Save conversation after successful execution
            messages = result["messages"]

            # Get AI response
            final_message = messages[-1]
            answer = extract_text(final_message)

            # Display AI response
            print("\nAI Agent:", answer, "\n")

        except Exception as error:

            print(
                "\nAI request failed:",
                type(error).__name__
            )

            print(
                "Please check your Gemini API quota "
                "or model connection.\n"
            )


# Start chatbot
if __name__ == "__main__":
    main()
