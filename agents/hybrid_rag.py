
from agents.rag_retriever import retrieve_faq
from agents.semantic_rag import semantic_search


def hybrid_search(query: str, top_k: int = 2) -> list[dict]:
    """
    Combine keyword and semantic FAQ retrieval.
    No customer account data is accessed.
    """
    if not query.strip() or top_k <= 0:
        return []

    keyword_results = retrieve_faq(query, top_k=top_k)
    semantic_results = semantic_search(query, top_k=top_k)

    combined = {}

    # Prefer reliable keyword matches initially.
    for rank, item in enumerate(keyword_results):
        combined[item["question"]] = {
            "question": item["question"],
            "answer": item["answer"],
            "rank_score": 2.0 / (rank + 1),
            "source": "keyword",
        }

    for rank, item in enumerate(semantic_results):
        question = item["question"]

        if question in combined:
            combined[question]["rank_score"] += 1.0 / (rank + 1)
            combined[question]["source"] = "keyword+semantic"
        else:
            combined[question] = {
                "question": question,
                "answer": item["answer"],
                "rank_score": 1.0 / (rank + 1),
                "source": "semantic",
            }

    ranked = sorted(
        combined.values(),
        key=lambda item: item["rank_score"],
        reverse=True
    )

    return ranked[:top_k]


if __name__ == "__main__":
    questions = [
        "Mera net bilkul nahi chal raha",
        "Mujhe internet ki shikayat darj karwani hai",
        "Mera wifi bohat slow hai",
        "What does a red LOS light mean?",
    ]

    for question in questions:
        print("\nCustomer:", question)

        results = hybrid_search(question)

        if not results:
            print("No relevant FAQ found.")
            continue

        for item in results:
            print("FAQ:", item["question"])
            print("Source:", item["source"])
            print("Rank score:", round(item["rank_score"], 3))
