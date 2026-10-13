from agents.ai_service import process_customer_message

session_id = "panel-voice-001"

messages = [
    "start connection check",
    "Falcon",
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