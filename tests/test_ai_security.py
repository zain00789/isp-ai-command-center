
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from agents.panel_session import panel_sessions

from tools.customer_tools import (
    get_customer_status,
    get_customer_package,
)
from tools.billing_tools import get_customer_bill


client = TestClient(app)


# TEST 1: AI support graph must not expose account tools
def test_account_tools_not_available_to_ai():
    from agents.support_graph import app as support_app

    graph = support_app.get_graph()
    node_names = set(graph.nodes.keys())

    assert "tools" not in node_names


# TEST 2: Direct account tools must deny access
def test_direct_account_tools_deny_access():
    account_tools = [
        get_customer_status,
        get_customer_package,
        get_customer_bill,
    ]

    for account_tool in account_tools:
        result = account_tool.invoke({
            "customer_id": "ISP001"
        })

        assert result["error"] == "authorization_required"


# TEST 3: Public AI conversation must not perform lookups
def test_public_ai_connection_flow_does_not_lookup_accounts():
    session_id = "security-test-001"
    panel_sessions.pop(session_id, None)

    # Patch the underlying account functions instead of
    # replacing StructuredTool.invoke on an instance.
    with (
        patch.object(
            get_customer_status,
            "func",
            side_effect=AssertionError(
                "Unauthorized status lookup"
            ),
        ),
        patch.object(
            get_customer_package,
            "func",
            side_effect=AssertionError(
                "Unauthorized package lookup"
            ),
        ),
        patch.object(
            get_customer_bill,
            "func",
            side_effect=AssertionError(
                "Unauthorized billing lookup"
            ),
        ),
    ):
        try:
            messages = [
                ("Mera internet nahi chal raha", "ask_panel"),
                ("Jazz", "ask_account"),
                ("ISP001", "verification_required"),
            ]

            for message, expected_action in messages:
                response = client.post(
                    "/api/v1/ai/respond",
                    json={
                        "session_id": session_id,
                        "message": message,
                    },
                )

                assert response.status_code == 200
                assert response.json()["action"] == expected_action

        finally:
            panel_sessions.pop(session_id, None)
