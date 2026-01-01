import re
from typing import Dict, Tuple


class IntentDetector:
    """
    Detects user intent from Hindi speech
    FIXED: Better Hindi keyword matching
    Compatible with existing main_app.py calls
    """

    def __init__(self, model_name: str = None):
        """
        Initialize with Hindi agricultural keywords

        Args:
            model_name: Optional model name (ignored, for compatibility)
        """

        # Accept model_name for compatibility but don't use it
        self.model_name = model_name

        # INTENT KEYWORDS - Hindi/English mixed
        self.intent_keywords = {
            "crop_loss": [
                "फसल खराब",
                "फसल बर्बाद",
                "फसल नष्ट",
                "crop loss",
                "crop destroyed",
                "crop damaged",
                "खराद",
                "नष्ट",
                "बर्बाद",
                "बर्बाद हो गई",
                "खराब हो गई",
                "नष्ट हो गई",
                # Sound-alike variations from speech recognition
                "बार",
                "खराब",
                "खराद हो",
            ],
            "pest_disease": [
                "कीट",
                "रोग",
                "बीमारी",
                "संक्रमण",
                "pest",
                "disease",
                "infection",
                "फसल में कीट",
                "फसल में रोग",
            ],
            "water_irrigation": [
                "पानी",
                "सिंचाई",
                "बोरवेल",
                "नलकूप",
                "water",
                "irrigation",
                "borewell",
            ],
            "soil_fertility": [
                "मिट्टी",
                "उर्वरता",
                "खाद",
                "जैव खाद",
                "soil",
                "fertility",
                "manure",
                "compost",
            ],
            "weather_damage": [
                "बाढ़",
                "सूखा",
                "ओलावृष्टि",
                "बारिश",
                "flood",
                "drought",
                "hail",
                "rain",
                "बर्षा",
                "बारिश की वजह से",
            ],
            "seed_quality": [
                "बीज",
                "गुणवत्ता",
                "रोपण",
                "नर्सरी",
                "seed",
                "quality",
                "planting",
            ],
            "financial_support": [
                "कर्ज",
                "लोन",
                "अनुदान",
                "सहायता",
                "loan",
                "grant",
                "subsidy",
                "support",
            ],
        }

        # DISASTER KEYWORDS - Hindi/English
        self.disaster_keywords = {
            "flood": [
                "बाढ़",
                "बाढ़ से",
                "बाढ़ी",
                "जलभराव",
                "flood",
                "flooding",
                "waterlogging",
            ],
            "drought": [
                "सूखा",
                "सूखे",
                "सूख",
                "पानी की कमी",
                "drought",
                "dry",
                "no water",
            ],
            "hail": [
                "ओलावृष्टि",
                "ओले",
                "ओला",
                "hail",
                "hailstorm",
            ],
            "heavy_rain": [
                "भारी बारिश",
                "अत्यधिक बारिश",
                "लंबी बारिश",
                "heavy rain",
                "excessive rain",
            ],
            "frost": [
                "पाला",
                "ठंड",
                "हिमपात",
                "frost",
                "cold",
                "freezing",
            ],
            "wind_damage": [
                "आंधी",
                "तूफान",
                "तेज हवा",
                "storm",
                "windstorm",
                "cyclone",
            ],
            "pest_infestation": [
                "कीट",
                "कीटों",
                "कीड़े",
                "pest",
                "insects",
            ],
            "disease": [
                "रोग",
                "बीमारी",
                "संक्रमण",
                "disease",
                "infection",
                "blight",
            ],
        }

    def detect(self, text: str) -> Dict:
        """
        Detect intent and disaster from text

        Args:
            text: Transcribed Hindi text

        Returns:
            Dict with intent, disaster, age, confidence
        """

        # Normalize text for matching
        text_lower = text.lower()

        # Extract age if present
        age = self._extract_age(text)

        # Find matching intents
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            matches = 0
            matched_keywords = []
            for keyword in keywords:
                # Case-insensitive search
                if keyword.lower() in text_lower:
                    matches += 1
                    matched_keywords.append(keyword)
            if matches > 0:
                intent_scores[intent] = matches
                if matched_keywords:
                    print(
                        f" Matched intent '{intent}' with keyword '{matched_keywords[0]}'"
                    )

        # Find matching disasters
        disaster_scores = {}
        for disaster, keywords in self.disaster_keywords.items():
            matches = 0
            matched_keywords = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches += 1
                    matched_keywords.append(keyword)
            if matches > 0:
                disaster_scores[disaster] = matches
                if matched_keywords:
                    print(
                        f" Matched disaster '{disaster}' with keyword '{matched_keywords[0]}'"
                    )

        # Get best matches
        best_intent = (
            max(intent_scores, key=intent_scores.get)
            if intent_scores
            else "general_support"
        )
        best_disaster = (
            max(disaster_scores, key=disaster_scores.get)
            if disaster_scores
            else "unspecified"
        )

        # Calculate confidence
        intent_score = intent_scores.get(best_intent, 0)
        disaster_score = disaster_scores.get(best_disaster, 0)

        # Print debug info
        if intent_score > 0:
            print(f" Best intent: {best_intent} (score: {intent_score})")

        if disaster_score > 0:
            print(f" Best disaster: {best_disaster} (score: {disaster_score})")

        # Boost confidence if both intent and disaster found
        confidence = 0.0
        if intent_score > 0 or disaster_score > 0:
            confidence = min(0.95, (intent_score + disaster_score) * 0.2)

        if best_intent != "general_support" and best_disaster != "unspecified":
            print(f" Boosted confidence for {best_intent} + {best_disaster}")
            confidence = 0.95

        return {
            "language": "hi",
            "intent": best_intent,
            "disaster": best_disaster,
            "age": age,
            "original_text": text,
            "confidence": confidence,
        }

    def parse_query(self, text: str) -> Dict:
        """
        Backwards-compatible wrapper for main_app.py.

        main_app.py expects:
            parsed_query = intent_detector.parse_query(text)

        This simply calls self.detect(text) and returns the same dict.
        """
        return self.detect(text)

    def _extract_age(self, text: str) -> int:
        """
        Extract age from Hindi text

        Examples:
        - "मेरी उमर पचास साल है" -> 50
        - "मेरी उमर ६५ साल है" -> 65
        """

        # Hindi number words
        hindi_numbers = {
            "शून्य": 0,
            "एक": 1,
            "दो": 2,
            "तीन": 3,
            "चार": 4,
            "पाँच": 5,
            "छः": 6,
            "सात": 7,
            "आठ": 8,
            "नौ": 9,
            "दस": 10,
            "ग्यारह": 11,
            "बारह": 12,
            "तेरह": 13,
            "चौदह": 14,
            "पन्द्रह": 15,
            "सोलह": 16,
            "सत्रह": 17,
            "अठारह": 18,
            "उन्नीस": 19,
            "बीस": 20,
            "तीस": 30,
            "चालीस": 40,
            "पचास": 50,
            "साठ": 60,
            "सत्तर": 70,
            "अस्सी": 80,
            "नब्बे": 90,
            "सौ": 100,
        }

        text_lower = text.lower()

        # Look for age-related patterns
        # "उमर", "सालों", "साल"
        age_patterns = [
            r"उम्र\s+(\d+)",
            r"उमर\s+(\d+)",
            r"(\d+)\s+साल",
            r"(\d+)\s+वर्ष",
        ]

        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return int(match.group(1))
                except Exception:
                    pass

        # Try Hindi number words
        for word, num in hindi_numbers.items():
            if f"{word} साल" in text_lower or f"{word} वर्ष" in text_lower:
                return num

        return 0


class SchemeFilter:
    """Filters eligible schemes based on detected intent/disaster"""

    def __init__(self, schemes: list = None):
        """
        Initialize with schemes

        Args:
            schemes: Optional list of schemes to filter
        """
        self.schemes = schemes or []

    def filter_eligible(self, intent: str, disaster: str, age: int = 0) -> list:
        """
        Filter schemes based on user profile

        Args:
            intent: Detected intent (crop_loss, pest_disease, etc.)
            disaster: Detected disaster (flood, drought, etc.)
            age: Farmer age

        Returns:
            List of eligible schemes
        """

        if not self.schemes:
            return []

        eligible = []

        for scheme in self.schemes:
            scheme_name = scheme.get("name", "").lower()
            scheme_desc = scheme.get("description", "").lower()

            # Check intent match
            intent_match = False
            if intent == "crop_loss":
                intent_match = (
                    "fasal" in scheme_name
                    or "crop" in scheme_desc
                    or "loss" in scheme_desc
                )
            elif intent == "pest_disease":
                intent_match = "pest" in scheme_desc or "disease" in scheme_desc
            elif intent == "water_irrigation":
                intent_match = "irrigation" in scheme_desc or "water" in scheme_desc
            elif intent == "soil_fertility":
                intent_match = "soil" in scheme_desc or "fertility" in scheme_desc
            else:
                intent_match = True  # general_support matches all

            # Check disaster match
            disaster_match = False
            if disaster == "flood":
                disaster_match = "flood" in scheme_desc or "water" in scheme_desc
            elif disaster == "drought":
                disaster_match = "drought" in scheme_desc or "dry" in scheme_desc
            elif disaster == "hail":
                disaster_match = "hail" in scheme_desc or "weather" in scheme_desc
            else:
                disaster_match = True  # unspecified matches all

            if intent_match or disaster_match:
                eligible.append(scheme)

        return eligible

