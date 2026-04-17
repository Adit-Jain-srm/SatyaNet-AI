import httpx
import json

resp = httpx.get("https://newsapi.org/v2/everything", params={
    "q": "UPI ban India",
    "apiKey": "7c57b7cc54fc4e0bbfd8150c77fb8dd5",
    "pageSize": 3,
    "sortBy": "relevancy",
    "language": "en",
}, timeout=10)
data = resp.json()
print("Status:", data.get("status"))
print("Total:", data.get("totalResults"))
for a in data.get("articles", [])[:3]:
    title = a.get("title", "")[:80]
    src = a.get("source", {}).get("name", "?")
    print(f"  - {title} | {src}")

print()
for q in ["5G COVID", "vaccine microchip", "modi free laptop"]:
    r2 = httpx.get("https://newsapi.org/v2/everything", params={
        "q": q, "apiKey": "7c57b7cc54fc4e0bbfd8150c77fb8dd5",
        "pageSize": 2, "sortBy": "relevancy",
    }, timeout=10)
    d2 = r2.json()
    print(f"{q}: {d2.get('totalResults', 0)} results, status={d2.get('status')}")
