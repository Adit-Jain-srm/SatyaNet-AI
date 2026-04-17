"""Smoke test for refined pipeline: URL fetching, processing log, Qdrant stats, cross-lingual."""
import httpx

API = "http://localhost:8000"
PASS = FAIL = 0

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f"  PASS  {name}")
    except Exception as e:
        FAIL += 1
        print(f"  FAIL  {name} -- {e}")

def analyze(content, content_type="text", timeout=90.0):
    r = httpx.post(f"{API}/analyze", json={"content": content, "content_type": content_type}, timeout=timeout)
    assert r.status_code == 200, f"HTTP {r.status_code}"
    return r.json()

print("=== Refined Pipeline Smoke Tests ===\n")

# Health
def t_health():
    r = httpx.get(f"{API}/health", timeout=10).json()
    assert r["qdrant_connected"]
test("Health", t_health)

# Processing log exists
def t_processing_log():
    r = analyze("UPI banned in India")
    assert "processing_log" in r
    assert len(r["processing_log"]) >= 5
    assert any("Language" in s for s in r["processing_log"])
    assert any("Qdrant" in s for s in r["processing_log"])
test("Processing log", t_processing_log)

# Qdrant stats
def t_qdrant_stats():
    r = analyze("5G towers cause COVID")
    stats = r.get("qdrant_stats", [])
    assert len(stats) == 3
    names = {s["collection"] for s in stats}
    assert "verified_facts" in names
    assert "misinfo_patterns" in names
    assert "source_credibility" in names
test("Qdrant stats", t_qdrant_stats)

# Detection method
def t_detection_method():
    r = analyze("hello world")
    assert "detection_method" in r
    assert r["detection_method"] in ("azure", "langdetect", "langdetect_fallback", "default", "azure_unavailable")
test("Detection method", t_detection_method)

# URL content type
def t_url_fetch():
    r = analyze("https://www.example.com", content_type="url")
    assert r["verdict"] in ("true", "false", "misleading", "unverified")
    log = r.get("processing_log", [])
    has_url_log = any("URL" in s for s in log)
    assert has_url_log, f"Expected URL log entry in: {log}"
test("URL fetch", t_url_fetch)

# Hindi with processing log
def t_hindi():
    r = analyze("\u0938\u0930\u0915\u093e\u0930 \u0928\u0947 UPI \u092a\u0930 \u092a\u094d\u0930\u0924\u093f\u092c\u0902\u0927 \u0932\u0917\u093e \u0926\u093f\u092f\u093e")
    assert r["detected_language"] == "hi"
    assert len(r["processing_log"]) > 0
test("Hindi analysis", t_hindi)

# Empty input
def t_empty():
    r = analyze("   ")
    assert r["verdict"] == "unverified"
    assert len(r["processing_log"]) > 0
test("Empty input", t_empty)

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
print(f"{'='*50}")
