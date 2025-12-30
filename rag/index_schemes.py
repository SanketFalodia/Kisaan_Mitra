import json
from chromadb import Client
from chromadb.config import Settings

client = Client(
    Settings(
        persist_directory="rag_db",
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection("schemes")

with open("data/uttarakhand_schemes.json", "r", encoding="utf-8") as f:
    schemes = json.load(f)

for scheme in schemes:
    document = f"""
    Scheme: {scheme['scheme_name']}
    Intent: {scheme['intent']}
    State: {scheme['state']}
    Age: {scheme['min_age']} to {scheme['max_age']}
    Disasters: {", ".join(scheme['allowed_disasters'])}
    """

    metadata = {
        "scheme_id": scheme["scheme_id"],
        "scheme_name": scheme["scheme_name"],
        "state": scheme["state"],
        "intent": scheme["intent"],
        "min_age": scheme["min_age"],
        "max_age": scheme["max_age"],
        "allowed_disasters": ",".join(scheme["allowed_disasters"]),
        "required_fields": ",".join(scheme["required_fields"]),
        "official_url": scheme["official_url"]
    }

    collection.add(
        documents=[document],
        metadatas=[metadata],
        ids=[scheme["scheme_id"]]
    )

print("✅ All schemes indexed into RAG")
