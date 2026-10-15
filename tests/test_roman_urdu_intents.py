
import pytest

from agents.intent_priority import detect_priority_intent


@pytest.mark.parametrize(
    "message, expected_intent",
    [
        ("Meri shikayat ki update dein", "ticket_status"),
        ("Complaint number ka kya bana?", "ticket_status"),
        ("Mujhe apna bill check karna hai", "billing"),
        ("Meri complaint band kar dein", "cancel_complaint"),
        ("Nayi shikayat likhwaani hai", "new_complaint"),
    ],
)
def test_roman_urdu_intent_detection(message, expected_intent):
    assert detect_priority_intent(message) == expected_intent


def test_empty_message_has_no_priority_intent():
    assert detect_priority_intent("") is None


def test_general_support_has_no_priority_intent():
    assert detect_priority_intent(
        "Mere router par red LOS light aa rahi hai"
    ) is None
