"""Live integration test — Google Fact Check end-to-end via running backend."""
import httpx

API = "http://127.0.0.1:8001"

CLAIMS = [
    "The COVID vaccine contains microchips to track people.",
    "Climate change is a hoax invented by China.",
    "The moon landing was faked by NASA in 1969.",
]

for claim in CLAIMS:
    resp = httpx.post(f"{API}/analyze", json={"content": claim, "content_type": "text"}, timeout=60)
    assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text}"
    data = resp.json()
    log = data.get("processing_log", [])
    ext = data.get("external_factchecks", [])
    gfc_line = next((l for l in log if "Google Fact Check" in l), "(missing)")

    print(f"\nClaim: {claim[:60]}")
    print(f"  {gfc_line}")
    print(f"  Overall verdict: {data['verdict']} ({data['credibility_score']:.0%})")
    for fc in ext[:2]:
        print(f"  [{fc['rating']}] {fc['publisher_name']}: {fc['claim_text'][:55]}")

    assert len(ext) > 0, f"FAIL: 0 external reviews returned for: {claim}"
    print("  PASS")

print("\nAll tests passed!")
