
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util

from agents.rag_retriever import load_faq


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def get_semantic_index():
    """
    Load the embedding model and FAQ vectors only
    when semantic search is first requested.

    Reuse them for subsequent requests.
    """

    model = SentenceTransformer(MODEL_NAME)

    faq_entries = load_faq()

    faq_texts = [
        f"{entry['question']} {entry['answer']}"
        for entry in faq_entries
    ]

    embeddings = model.encode(
        faq_texts,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    return model, faq_entries, embeddings


def semantic_search(
    query: str,
    top_k: int = 2,
    min_score: float = 0.45
) -> list[dict]:
    """
    Retrieve general ISP FAQs using semantic similarity.

    No customer account data is accessed.
    """

    if not query or not query.strip() or top_k <= 0:
        return []

    model, faq_entries, faq_embeddings = get_semantic_index()

    if not faq_entries:
        return []

    query_embedding = model.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarities = util.cos_sim(
        query_embedding,
        faq_embeddings
    )[0]

    ranked_indices = similarities.argsort(
        descending=True
    ).tolist()

    results = []

    for index in ranked_indices[:top_k]:
        score = float(similarities[index])

        if score >= min_score:
            results.append({
                "question": faq_entries[index]["question"],
                "answer": faq_entries[index]["answer"],
                "score": round(score, 3)
            })

    return results


if __name__ == "__main__":
    questions = [
        "Mera net bilkul nahi chal raha",
        "Mujhe internet ki shikayat darj karwani hai",
        "Mera wifi bohat slow hai",
    ]

    for question in questions:
        print("\nCustomer:", question)

        results = semantic_search(question)

        for result in results:
            print("Matched FAQ:", result["question"])
            print("Similarity:", result["score"])
