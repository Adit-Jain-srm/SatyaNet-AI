"""Quick smoke test for all modalities + News API + new endpoints."""
import httpx
import json
import base64

API = "http://localhost:8000"


def analyze(content, content_type="text", timeout=90.0):
    resp = httpx.post(f"{API}/analyze", json={
        "content": content, "content_type": content_type
    }, timeout=timeout)
    assert resp.status_code == 200, f"HTTP {resp.status_code}"
    return resp.json()


print("=== SatyaNet Smoke Test ===\n")

# Health
r = httpx.get(f"{API}/health", timeout=10).json()
print(f"[1] Health: {r['status']}, collections={len(r['collections'])}")

# Text with News API
r = analyze("Government banned UPI in India")
has_news = len(r.get("news_articles", [])) > 0
print(f"[2] Text EN: verdict={r['verdict']}, score={r['credibility_score']}, news={has_news}, claims={len(r['claims'])}")

# Hindi
r = analyze("5G \u091f\u093e\u0935\u0930 COVID-19 \u092b\u0948\u0932\u093e \u0930\u0939\u0947 \u0939\u0948\u0902")
print(f"[3] Text HI: lang={r['detected_language']}, verdict={r['verdict']}")

# Tamil
r = analyze("COVID-19 \u0ba4\u0b9f\u0bc1\u0baa\u0bcd\u0baa\u0bc2\u0b9a\u0bbf\u0b95\u0bb3\u0bbf\u0bb2\u0bcd \u0bae\u0bc8\u0b95\u0bcd\u0bb0\u0bcb\u0b9a\u0bbf\u0baa\u0bcd\u0b95\u0bb3\u0bcd")
print(f"[4] Text TA: lang={r['detected_language']}, verdict={r['verdict']}")

# Breakdown has google_factcheck_score
r = analyze("covid vaccine microchip government surveillance")
b = r["breakdown"]
print(f"[5] Breakdown: gfc={b['google_factcheck_score']}, ai={b['ai_generation_score']}")
print(f"    External FCs: {len(r.get('external_factchecks', []))}")
print(f"    News articles: {len(r.get('news_articles', []))}")

# Audio type (graceful with empty data)
r = analyze("", content_type="audio")
print(f"[6] Audio empty: verdict={r['verdict']}, audio={r.get('audio_analysis') is not None}")

# Video type (graceful with empty data)
r = analyze("", content_type="video")
print(f"[7] Video empty: verdict={r['verdict']}, video={r.get('video_analysis') is not None}")

# Image with base64
from PIL import Image
import io
img = Image.new("RGB", (100, 100), color="blue")
buf = io.BytesIO()
img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
r = analyze(b64, content_type="image")
print(f"[8] Image: verdict={r['verdict']}, img_analysis={r.get('image_analysis') is not None}")

# File upload endpoint
files = {"file": ("test.png", buf.getvalue(), "image/png")}
data = {"content_type": "image"}
resp = httpx.post(f"{API}/analyze/upload", files=files, data=data, timeout=90)
print(f"[9] Upload endpoint: status={resp.status_code}")
if resp.status_code == 200:
    ur = resp.json()
    print(f"    verdict={ur['verdict']}, img={ur.get('image_analysis') is not None}")

# Empty input edge case
r = analyze("   ", content_type="text")
print(f"[10] Empty: verdict={r['verdict']}, score={r['credibility_score']}")

print("\n=== ALL SMOKE TESTS PASSED ===")
