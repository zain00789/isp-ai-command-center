from agents.ai_service import process_customer_message

session_id = "test-session-001"

print("\n--- First customer message ---")

result1 = process_customer_message(
    message="Assalam-o-Alaikum, mera internet slow hai.",
    session_id=session_id
)

print("Intent:", result1["intent"])
print("AI:", result1["response"])

print("\n--- Second customer message ---")

result2 = process_customer_message(
    message="Mera customer ID ISP001 hai.",
    session_id=session_id
)

print("Intent:", result2["intent"])
print("AI:", result2["response"])