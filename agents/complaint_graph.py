from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from tools.verification_tools import check_customer_record
from tools.ticket_tools import create_support_ticket
from tools.message_tools import send_test_message

# 1. Information shared between workflow steps
class ComplaintState(TypedDict):
    customer_id: str
    phone: str
    issue: str
    confirmed: bool
    matched: bool
    result: str
    ticket_id: str
    message_status: str

# 2. Check fictional customer record
def check_customer(state: ComplaintState):

    response = check_customer_record.invoke({
        "customer_id": state["customer_id"],
        "phone": state["phone"]
    })

    print("Customer record matched:", response["match"])

    return {"matched": response["match"]}


# 3. Decide whether to continue

def check_permission(state: ComplaintState):
    """
    Temporary deny-by-default authorization.

    A matching customer ID and phone number does not
    prove that the caller owns the account.
    """

    # Do not create tickets without trusted
    # backend customer authentication.
    return "rejected"



# 4. Create fictional support ticket
def create_ticket(state: ComplaintState):

    response = create_support_ticket.invoke({
        "customer_id": state["customer_id"],
        "issue": state["issue"]
    })

    return {
        "ticket_id": response["ticket_id"],
        "result": f"Ticket created: {response['ticket_id']}"
    }

def send_confirmation(state: ComplaintState):

    response = send_test_message.invoke({
        "customer_id": state["customer_id"],
        "ticket_id": state["ticket_id"]
    })

    print("Message:", response["message"])

    return {
        "message_status": response["status"]
    }
# 5. Handle rejected request
def reject_request(state: ComplaintState):
    return {
        "result": (
            "Ticket not created. "
            "Secure customer verification is required."
        ),
        "ticket_id": "",
        "message_status": ""
    }

# 6. Build LangGraph
workflow = StateGraph(ComplaintState)

workflow.add_node("check_customer", check_customer)
workflow.add_node("create_ticket", create_ticket)
workflow.add_node("send_confirmation", send_confirmation)
workflow.add_node("reject_request", reject_request)
workflow.add_edge(START, "check_customer")

workflow.add_conditional_edges(
    "check_customer",
    check_permission,
    {
        "approved": "create_ticket",
        "rejected": "reject_request"
    }
)
workflow.add_edge("create_ticket", "send_confirmation")
workflow.add_edge("send_confirmation", END)
workflow.add_edge("reject_request", END)

app = workflow.compile()


# 7. Test with fictional data only
if __name__ == "__main__":

    print("\n===== ISP AI Complaint System =====\n")

    # Ask for customer information
    customer_id = input("Enter customer ID: ").strip()
    phone = input("Enter registered phone: ").strip()
    issue = input("Describe your issue: ").strip()

    # Ask for explicit confirmation
    confirmation = input(
        "Confirm complaint registration (yes/no): "
    ).strip().lower()

    confirmed = confirmation == "yes"

    # Run LangGraph workflow
    result = app.invoke({
        "customer_id": customer_id,
        "phone": phone,
        "issue": issue,
        "confirmed": confirmed,
        "matched": False,
        "result": "",
        "ticket_id": "",
        "message_status": ""
    })

    print("\nFinal result:", result["result"])
    print("Message status:", result["message_status"])