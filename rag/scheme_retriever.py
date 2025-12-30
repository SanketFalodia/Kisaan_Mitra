from chromadb import Client
from chromadb.config import Settings

client = Client(
    Settings(
        persist_directory="rag_db",
        anonymized_telemetry=False
    )
)

collection = client.get_collection("schemes")

def get_eligible_schemes(intent, disaster, age, state="Uttarakhand"):
    query = f"{intent} {disaster} farmer age {age} {state}"
    results = collection.query(query_texts=[query], n_results=5)

    eligible = []

    for meta in results["metadatas"][0]:
        allowed_disasters = meta["allowed_disasters"].split(",")

        if (
            meta["min_age"] <= age <= meta["max_age"]
            and disaster in allowed_disasters
            and (meta["state"] == state or meta["state"] == "ALL")
        ):
            eligible.append({
                "scheme_name": meta["scheme_name"],
                "required_fields": meta["required_fields"].split(","),
                "official_url": meta["official_url"]
            })

    return eligible
