import os
import json
from typing import List, Dict, Optional
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from datetime import datetime


# Language codes
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "garhwali": "Garhwali",
    "kumaoni": "Kumaoni",
    "en": "English"
}


class MultilingualSchemeRetriever:
    """
    RAG system for scheme retrieval with multilingual support
    FIXED: Better intent/disaster matching
    """
    
    def __init__(self, db_path: str = "rag_db"):
        self.db_path = db_path
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Initialize ChromaDB
        self.client = Client(
            Settings(
                persist_directory=os.path.join(self.base_dir, db_path),
                anonymized_telemetry=False
            )
        )
        
        # Initialize embedding model (multilingual)
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="schemes_multilingual",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize schemes
        self._initialize_schemes()
    
    def _initialize_schemes(self):
        """Load and index schemes from JSON"""
        data_path = os.path.join(self.base_dir, "data", "uttarakhand_schemes.json")
        
        if len(self.collection.get()["ids"]) == 0:
            print("⚡ Indexing Uttarakhand schemes into ChromaDB...")
            
            with open(data_path, "r", encoding="utf-8") as f:
                schemes = json.load(f)
            
            for scheme in schemes:
                # Create comprehensive document
                document = f"""
                Scheme: {scheme['scheme_name']}
                Intent: {scheme['intent']}
                State: {scheme['state']}
                Age Eligibility: {scheme['min_age']} to {scheme['max_age']} years
                Allowed Disasters: {', '.join(scheme['allowed_disasters'])}
                Required Documents: {', '.join(scheme['required_fields'])}
                """
                
                # Metadata with all required info
                metadata = {
                    "scheme_id": scheme["scheme_id"],
                    "scheme_name": scheme["scheme_name"],
                    "state": scheme["state"],
                    "intent": scheme["intent"],
                    "min_age": scheme["min_age"],
                    "max_age": scheme["max_age"],
                    "allowed_disasters": ",".join(scheme["allowed_disasters"]),
                    "required_fields": ",".join(scheme["required_fields"]),
                    "official_url": scheme["official_url"],
                    "indexed_at": datetime.now().isoformat(),
                    "language": "multilingual"
                }
                
                self.collection.add(
                    documents=[document],
                    metadatas=[metadata],
                    ids=[scheme["scheme_id"]]
                )
            
            print("✅ All schemes indexed successfully!")
    
    def get_eligible_schemes(
        self,
        intent: str,
        disaster: str,
        age: int,
        state: str = "Uttarakhand",
        language: str = "hi"
    ) -> List[Dict]:
        """
        Retrieve eligible schemes based on farmer criteria
        
        Args:
            intent: Type of support needed (e.g., 'crop_loss', 'farming_support')
            disaster: Type of disaster (e.g., 'flood', 'drought')
            age: Farmer's age
            state: State (default: Uttarakhand)
            language: Language code (hi, garhwali, kumaoni, en)
        
        Returns:
            List of eligible schemes with translated names
        """
        
        # Map detected intents to scheme intents
        intent_map = {
            'crop_loss': ['crop_insurance', 'agri_development', 'income_support'],
            'pest_disease': ['agri_extension', 'pest_management', 'agri_development'],
            'water_irrigation': ['irrigation_support', 'agri_infrastructure', 'agri_development'],
            'soil_fertility': ['soil_testing', 'agri_development'],
            'weather_damage': ['crop_insurance', 'agri_development', 'disaster_relief'],
            'seed_quality': ['agri_extension', 'agri_development'],
            'financial_support': ['agri_credit', 'income_support', 'pension_support'],
            'general_support': ['agri_development', 'income_support', 'agri_credit', 'crop_insurance'],
        }
        
        # Map detected disasters to scheme disasters
        disaster_map = {
            'flood': ['flood'],
            'drought': ['drought'],
            'hail': ['hailstorm'],
            'heavy_rain': ['flood'],
            'frost': ['hailstorm'],
            'wind_damage': ['cyclone'],
            'pest_infestation': ['pest_attack'],
            'disease': ['disease'],
            'unspecified': None,  # Accept all
        }
        
        # Get matching intents and disasters
        matching_intents = intent_map.get(intent, [intent])
        matching_disasters = disaster_map.get(disaster, [disaster])
        
        print(f"🎯 Looking for intents: {matching_intents}")
        if matching_disasters:
            print(f"🎯 Looking for disasters: {matching_disasters}")
        
        # Get ALL schemes first
        all_results = self.collection.get(include=["metadatas"])
        eligible_schemes = []
        
        if not all_results["metadatas"]:
            return eligible_schemes
        
        # Filter schemes based on criteria
        for meta in all_results["metadatas"]:
            scheme_intent = meta.get("intent", "").lower()
            allowed_disasters = [d.strip().lower() for d in meta.get("allowed_disasters", "").split(",")]
            min_age = meta.get("min_age", 0)
            max_age = meta.get("max_age", 99)
            state_meta = meta.get("state", "ALL")
            
            # Check intent match
            intent_match = any(
                mi.lower() in scheme_intent or scheme_intent in mi.lower()
                for mi in matching_intents
            )
            
            if not intent_match:
                print(f"⏭️ {meta['scheme_name']}: intent '{scheme_intent}' doesn't match {matching_intents}")
                continue
            
            # Check disaster match (if specified)
            if matching_disasters:
                disaster_match = any(
                    md.lower() in allowed_disasters or d in md.lower()
                    for md in matching_disasters
                    for d in allowed_disasters
                )
            else:
                # No specific disaster, accept all
                disaster_match = True
            
            if not disaster_match:
                print(f"⏭️ {meta['scheme_name']}: disaster doesn't match. Allowed: {allowed_disasters}, Looking for: {matching_disasters}")
                continue
            
            # Check age match
            if age > 0 and not (min_age <= age <= max_age):
                print(f"⏭️ {meta['scheme_name']}: age {age} outside range {min_age}-{max_age}")
                continue
            
            # Check state match
            if state_meta != "ALL" and state_meta.lower() != state.lower():
                print(f"⏭️ {meta['scheme_name']}: state mismatch")
                continue
            
            # All checks passed!
            scheme_data = {
                "scheme_id": meta.get("scheme_id"),
                "scheme_name": meta.get("scheme_name"),
                "intent": meta.get("intent"),
                "required_fields": [f.strip() for f in meta.get("required_fields", "").split(",")],
                "official_url": meta.get("official_url"),
                "allowed_disasters": allowed_disasters,
                "age_eligibility": f"{min_age} - {max_age} years"
            }
            eligible_schemes.append(scheme_data)
            print(f"✅ Eligible: {meta.get('scheme_name')}")
        
        print(f"📚 Total eligible schemes: {len(eligible_schemes)}")
        return eligible_schemes
    
    def get_scheme_details(self, scheme_id: str) -> Optional[Dict]:
        """Get detailed information about a specific scheme"""
        results = self.collection.get(ids=[scheme_id])
        
        if not results["metadatas"] or len(results["metadatas"]) == 0:
            return None
        
        meta = results["metadatas"][0]
        return {
            "scheme_id": meta["scheme_id"],
            "scheme_name": meta["scheme_name"],
            "state": meta["state"],
            "intent": meta["intent"],
            "min_age": meta["min_age"],
            "max_age": meta["max_age"],
            "allowed_disasters": meta["allowed_disasters"].split(","),
            "required_fields": meta["required_fields"].split(","),
            "official_url": meta["official_url"]
        }
    
    def add_new_scheme(self, scheme_data: Dict) -> bool:
        """Add a new scheme to the database"""
        try:
            document = f"""
            Scheme: {scheme_data['scheme_name']}
            Intent: {scheme_data['intent']}
            State: {scheme_data['state']}
            Age Eligibility: {scheme_data['min_age']} to {scheme_data['max_age']} years
            """
            
            metadata = {
                "scheme_id": scheme_data["scheme_id"],
                "scheme_name": scheme_data["scheme_name"],
                "state": scheme_data["state"],
                "intent": scheme_data["intent"],
                "min_age": scheme_data["min_age"],
                "max_age": scheme_data["max_age"],
                "allowed_disasters": ",".join(scheme_data.get("allowed_disasters", [])),
                "required_fields": ",".join(scheme_data.get("required_fields", [])),
                "official_url": scheme_data.get("official_url", ""),
                "indexed_at": datetime.now().isoformat()
            }
            
            self.collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[scheme_data["scheme_id"]]
            )
            
            return True
        except Exception as e:
            print(f"Error adding scheme: {e}")
            return False



# Initialize global retriever
retriever = MultilingualSchemeRetriever()