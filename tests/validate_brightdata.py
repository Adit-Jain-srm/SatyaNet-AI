"""Validate Bright Data SERP API connectivity and response format."""
import httpx
import json

API_TOKEN = "3b03dc38-55dc-4ff9-b9bc-c6f1fbe3108a"
SERP_ZONE = "serp_api1"
ENDPOINT = "https://api.brightdata.com/request"

query = "India Prime Minister 2024"
google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num=5"

print(f"Testing Bright Data SERP API...")
print(f"  Zone: {SERP_ZONE}")
print(f"  Query: {query}")
print(f"  URL: {google_url}")
print()

try:
    resp = httpx.post(
        ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}",
        },
        json={
            "zone": SERP_ZONE,
            "url": google_url,
            "format": "json",
        },
        timeout=30.0,
    )
    print(f"HTTP Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("SUCCESS - response keys:", list(data.keys()) if isinstance(data, dict) else type(data))
        # Show organic results if present
        organic = data.get("organic", [])
        if organic:
            print(f"\nOrganic results ({len(organic)}):")
            for r in organic[:3]:
                print(f"  - {r.get('title', '')[:60]}")
                print(f"    {r.get('link', '')[:80]}")
        else:
            print("Raw response (first 500 chars):", str(data)[:500])
    else:
        print("FAILED response:", resp.text[:500])
except Exception as e:
    print(f"ERROR: {e}")

# Also test with a different format (raw HTML)
print("\n--- Testing raw format ---")
try:
    resp2 = httpx.post(
        ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}",
        },
        json={
            "zone": SERP_ZONE,
            "url": google_url,
        },
        timeout=30.0,
    )
    print(f"HTTP Status: {resp2.status_code}")
    if resp2.status_code == 200:
        content = resp2.text
        # Check if Modi appears in results  
        if "Modi" in content:
            print("SUCCESS - 'Modi' found in search results!")
        else:
            print("WARNING - 'Modi' not found in results")
        print(f"Response length: {len(content)} chars")
        # Try to find title-like content
        import re
        titles = re.findall(r'"title"\s*:\s*"([^"]{10,80})"', content)
        if titles:
            print("Titles found:", titles[:5])
    else:
        print("FAILED:", resp2.text[:300])
except Exception as e:
    print(f"ERROR: {e}")
