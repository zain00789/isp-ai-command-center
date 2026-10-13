from agents.ai_service import process_customer_message

session_id = "natural-panel-test-001"

messages = [
    "Mera internet nahi chal raha",
    "Jazz",
    "ISP001"
]

for message in messages:
    print("\nCustomer:", message)

    result = process_customer_message(
        message=message,
        session_id=session_id
    )

    print("AI:", result["response"])
    print("Action:", result["action"])