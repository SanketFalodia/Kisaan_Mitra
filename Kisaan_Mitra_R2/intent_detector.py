def detect_intent(text: str) -> str:
    text = text.lower()

    if any(k in text for k in ["बाढ़", "सूखा", "फसल", "नुकसान", "खराब"]):
        return "crop_loss"

    if any(k in text for k in ["बीमा", "insurance"]):
        return "insurance"

    if any(k in text for k in ["लोन", "loan", "ऋण"]):
        return "loan"

    if any(k in text for k in ["सब्सिडी", "subsidy"]):
        return "subsidy"

    return "general_query"
