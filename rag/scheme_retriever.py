# scheme_retriever.py

import os
import json
from chromadb import Client
from chromadb.config import Settings

# ------------------------------
# Paths
# ------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rag_db")
DATA_PATH = os.path.join(BASE_DIR, "data", "uttarakhand_schemes.json")

# ------------------------------
# Initialize ChromaDB client
# ------------------------------
client = Client(
    Settings(
        persist_directory=DB_PATH,
        anonymized_telemetry=False
    )
)

# ------------------------------
# Get or create collection
# ------------------------------
collection = client.get_or_create_collection("schemes")

# ------------------------------
# If collection is empty, index the JSON data
# ------------------------------
if len(collection.get()["ids"]) == 0:
    print("⚡ 'schemes' collection is empty. Indexing Uttarakhand schemes...")
    
    with open(DATA_PATH, "r", encoding="utf-8") as f:
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
    print("✅ Uttarakhand schemes indexed successfully!")

# ------------------------------
# Function to get eligible schemes
# ------------------------------
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
