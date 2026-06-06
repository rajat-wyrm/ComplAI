import requests
import json

url = "http://localhost:8000/api/upload"
file_path = "sample_compliance_document.txt"

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "text/plain")}
    response = requests.post(url, files=files)

result = response.json()
print(json.dumps(result, indent=2))
if result.get("success"):
    print("\n✅ Upload successful!")
    print("Document ID:", result["document_id"])
    print("Risk Score:", result["report"]["risk_score"])
    print("Compliance Score:", result["report"]["compliance_score"])
    print("\nOpening dashboard...")
    import webbrowser
    webbrowser.open(f"http://localhost:3001/dashboard?docId={result['document_id']}")
else:
    print("❌ Upload failed:", result.get("error"))
