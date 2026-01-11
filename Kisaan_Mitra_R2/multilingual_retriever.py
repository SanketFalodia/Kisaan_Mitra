import json

DATA_PATH = r"data\uttarakhand_schemes.json"

def load_schemes():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def retrieve_schemes(query: str, intent: str, top_k: int = 3):
    schemes = load_schemes()
    results = []

    query_words = query.lower().split()

    for scheme in schemes:
        text = (
            scheme.get("name", "") +
            scheme.get("description", "") +
            scheme.get("category", "")
        ).lower()

        if intent in text or any(w in text for w in query_words):
            results.append(scheme)

    return results[:top_k]
