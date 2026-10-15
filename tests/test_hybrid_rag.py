
from agents.hybrid_rag import hybrid_search


def test_hybrid_internet_problem():
    results = hybrid_search(
        "Mera net bilkul nahi chal raha"
    )

    assert results
    assert "internet is not working" in results[0]["question"].lower()


def test_hybrid_complaint():
    results = hybrid_search(
        "Mujhe internet ki shikayat darj karwani hai"
    )

    assert results
    assert "register a complaint" in results[0]["question"].lower()


def test_hybrid_slow_wifi():
    results = hybrid_search(
        "Mera wifi bohat slow hai"
    )

    assert results
    assert "wi-fi is slow" in results[0]["question"].lower()


def test_hybrid_red_los():
    results = hybrid_search(
        "What does a red LOS light mean?"
    )

    assert results
    assert "red los" in results[0]["question"].lower()
