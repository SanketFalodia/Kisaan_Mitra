from rag.scheme_retriever import get_eligible_schemes

result = get_eligible_schemes(
    intent="crop_loss",
    disaster="flood",
    age=68,
    state="Uttarakhand"
)

for s in result:
    print("Eligible:", s["scheme_name"])