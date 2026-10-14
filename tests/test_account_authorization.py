
from fastapi.testclient import TestClient

from backend.main import app
from backend.authorization import is_customer_authorized

from tools.customer_tools import (
    get_customer_status,
    get_customer_package,
)
from tools.billing_tools import get_customer_bill


client = TestClient(app)


# TEST 1: Unverified API access must be denied
def test_unverified_customer_status_is_forbidden():
    response = client.get(
        "/api/v1/customers/ISP001/status"
    )

    assert response.status_code == 403


# TEST 2: Direct customer status tool access
def test_customer_status_tool_requires_authorization():
    result = get_customer_status.invoke({
        "customer_id": "ISP001"
    })

    assert result["error"] == "authorization_required"
    assert "connection_status" not in result


# TEST 3: Direct package tool access
def test_customer_package_tool_requires_authorization():
    result = get_customer_package.invoke({
        "customer_id": "ISP001"
    })

    assert result["error"] == "authorization_required"
    assert "package" not in result


# TEST 4: Direct billing tool access
def test_customer_bill_tool_requires_authorization():
    result = get_customer_bill.invoke({
        "customer_id": "ISP001"
    })

    assert result["error"] == "authorization_required"
    assert "amount" not in result
    assert "currency" not in result
    assert "payment_status" not in result
    assert "due_date" not in result


# TEST 5: Customer ID alone is not verification
def test_customer_id_alone_is_not_authorization():
    result = is_customer_authorized(
        customer_id="ISP001",
        session_id=""
    )

    assert result is False


# TEST 6: A random session ID is not verification
def test_session_id_does_not_prove_identity():
    result = is_customer_authorized(
        customer_id="ISP001",
        session_id="random_session_123"
    )

    assert result is False


# TEST 7: Unknown accounts must not be authorized
def test_unknown_customer_is_not_authorized():
    result = is_customer_authorized(
        customer_id="UNKNOWN999",
        session_id="test_session"
    )

    assert result is False


# TEST 8: Empty customer IDs must be rejected
def test_empty_customer_id_is_not_authorized():
    result = is_customer_authorized(
        customer_id="",
        session_id="test_session"
    )

    assert result is False


# TEST 9: Empty session IDs must not grant access
def test_empty_session_id_is_not_authorized():
    result = is_customer_authorized(
        customer_id="ISP001",
        session_id=""
    )

    assert result is False
