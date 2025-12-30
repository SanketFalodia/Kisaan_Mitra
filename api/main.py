from fastapi import FastAPI
from pydantic import BaseModel
from rag.scheme_retriever import get_eligible_schemes

app = FastAPI(title="Voice Mitra RAG API")

class FarmerQuery(BaseModel):
    intent: str
    disaster: str
    age: int

@app.post("/recommend-scheme")
def recommend_scheme(data: FarmerQuery):
    schemes = get_eligible_schemes(
        intent=data.intent,
        disaster=data.disaster,
        age=data.age
    )

    if not schemes:
        return {"message": "No eligible scheme found"}

    return {
        "recommended_schemes": [
            {
                "scheme_name": s["scheme_name"],
                "required_fields": s["required_fields"],
                "official_url": s["official_url"]
            }
            for s in schemes
        ]
    }