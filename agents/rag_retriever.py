
from pathlib import Path
import re


# Knowledge base location
BASE_DIR = Path(__file__).resolve().parent.parent
FAQ_PATH = BASE_DIR / "knowledge_base" / "isp_faq.txt"


def load_faq() -> list[dict]:
    """Read FAQ questions and answers."""

    if not FAQ_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {FAQ_PATH}"
        )

    text = FAQ_PATH.read_text(encoding="utf-8")

    entries = []
    current_question = None

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("Q:"):
            current_question = line[2:].strip()

        elif line.startswith("A:") and current_question:
            entries.append({
                "question": current_question,
                "answer": line[2:].strip()
            })
            current_question = None

    return entries


# Common words that are not useful for searching
STOP_WORDS = {
    "a", "an", "the", "is", "are", "what", "how",
    "do", "does", "if", "i", "my", "me", "can",
    "should", "to", "for", "of", "in", "on",
    "and", "it", "be", "when", "with",
    "mera", "meri", "mere", "mujhe", "hai",
    "ka", "ki", "ke", "kar", "raha", "rahi",
    "bilkul", "apna", "apne"
}


# Roman Urdu to English vocabulary
ROMAN_URDU_WORDS = {
    "net": "internet",
    "nahi": "not",
    "chal": "working",
    "shikayat": "complaint",
    "darj": "register",
    "karwani": "register",
    "laal": "red",
    "yaad": "remember",
    "bhool": "forgotten",
    "masla": "problem",
    "band": "not working",
}


def tokenize(text: str) -> set[str]:
    """Convert English and Roman Urdu into searchable words."""

    words = re.findall(r"[a-z0-9]+", text.lower())

    tokens = set()

    for word in words:
        if word in STOP_WORDS:
            continue

        translated = ROMAN_URDU_WORDS.get(word, word)

        for token in re.findall(r"[a-z0-9]+", translated):
            if token not in STOP_WORDS:
                tokens.add(token)

    return tokens


def retrieve_faq(query: str, top_k: int = 2) -> list[dict]:
    """Find relevant FAQs using keyword matching."""

    query_words = tokenize(query)

    if not query_words or top_k <= 0:
        return []

    scored_entries = []

    for entry in load_faq():
        question_words = tokenize(entry["question"])
        answer_words = tokenize(entry["answer"])

        # Question matches are more important
        score = (
            3 * len(query_words & question_words)
            + len(query_words & answer_words)
        )

        if score >= 4:
            scored_entries.append((score, entry))

    # Sort from highest score to lowest
    scored_entries.sort(
        key=lambda item: item[0],
        reverse=True
    )

    if not scored_entries:
        return []

    # Highest relevance score
    best_score = scored_entries[0][0]

    # Keep only sufficiently relevant results
    filtered_entries = [
        entry
        for score, entry in scored_entries
        if score >= best_score * 0.75
    ]

    return filtered_entries[:top_k]


if __name__ == "__main__":
    questions = [
        "What does a red LOS light mean?",
        "My Wi-Fi is slow",
        "How can I register a complaint?",
        "Mera net bilkul nahi chal raha",
        "Mujhe internet ki shikayat darj karwani hai",
    ]

    for question in questions:
        print("\nCustomer:", question)

        results = retrieve_faq(question)

        if not results:
            print("No relevant FAQ found.")
            continue

        for result in results:
            print("Matched FAQ:", result["question"])
            print("Answer:", result["answer"])
