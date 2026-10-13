from langchain_core.messages import HumanMessage, AIMessage

from agents.support_graph import guarded_tools


def test_lookup(customer_message, requested_id):
    customer = HumanMessage(content=customer_message)

    tool_request = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_customer_status",
                "args": {"customer_id": requested_id},
                "id": "test-call-001",
                "type": "tool_call",
            }
        ],
    )

    result = guarded_tools({
        "messages": [customer, tool_request]
    })

    print("Customer message:", customer_message)
    print("Requested customer ID:", requested_id)
    print("Tool result:", result["messages"][0].content)
    print("-" * 50)


print("\nTEST 1: Invented customer ID")
test_lookup(
    "Mera internet slow hai",
    "ISP001"
)

print("\nTEST 2: Customer-supplied ID")
test_lookup(
    "Mera customer ID ISP001 hai",
    "ISP001"
)

print("\nTEST 3: Different customer ID")
test_lookup(
    "Mera customer ID ISP001 hai",
    "ISP002"
)