
from agents.rag_retriever import retrieve_faq


def test_english_los_question():
    results = retrieve_faq(
        "What does a red LOS light mean?"
    )

    assert results
    assert "red LOS" in results[0]["question"]


def test_english_wifi_question():
    results = retrieve_faq(
        "My Wi-Fi is slow"
    )

    assert results
    assert "Wi-Fi is slow" in results[0]["question"]


def test_roman_urdu_los_question():
    results = retrieve_faq(
        "Mere router par laal light aa rahi hai"
    )

    assert results
    assert "red LOS" in results[0]["question"]


def test_roman_urdu_wifi_question():
    results = retrieve_faq(
        "Mera Wi-Fi bohat slow hai"
    )

    assert results
    assert "Wi-Fi is slow" in results[0]["question"]

def test_roman_urdu_internet_not_working():
    results = retrieve_faq(
        "Mera net bilkul nahi chal raha"
    )

    assert results
    assert "internet is not working" in results[0]["question"]


def test_roman_urdu_password():
    results = retrieve_faq(
        "Mujhe apne wifi ka password yaad nahi"
    )

    assert results
    assert "password is forgotten" in results[0]["question"]


def test_roman_urdu_complaint():
    results = retrieve_faq(
        "Mujhe internet ki shikayat darj karwani hai"
    )

    assert results
    assert "register a complaint" in results[0]["question"]