# test_rag.py

from rag.scheme_retriever import get_eligible_schemes

# ------------------------------
# Test input
# ------------------------------
test_queries = [
    {"intent": "crop_loss", "disaster": "flood", "age": 68, "state": "Uttarakhand"},
    {"intent": "livestock_loss", "disaster": "drought", "age": 45, "state": "Uttarakhand"},
    {"intent": "farming_support", "disaster": "storm", "age": 30, "state": "Uttarakhand"},
]

# ------------------------------
# Run queries and display results
# ------------------------------
for i, query in enumerate(test_queries, start=1):
    print(f"\n--- Query {i} ---")
    print(f"Intent: {query['intent']}, Disaster: {query['disaster']}, Age: {query['age']}, State: {query['state']}")
    
    results = get_eligible_schemes(
        intent=query["intent"],
        disaster=query["disaster"],
        age=query["age"],
        state=query["state"]
    )
    
    if not results:
        print("No eligible schemes found.")
    else:
        for j, scheme in enumerate(results, start=1):
            print(f"{j}. Scheme Name: {scheme['scheme_name']}")
            print(f"   Required Fields: {', '.join(scheme['required_fields'])}")
            print(f"   Official URL: {scheme['official_url']}")