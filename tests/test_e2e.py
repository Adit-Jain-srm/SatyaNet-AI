"""End-to-end tests for SatyaNet-AI pipeline."""

import sys
import httpx
import json
import base64

API = "http://localhost:8000"
PASS = 0
FAIL = 0


def test(name: str, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f"  PASS  {name}")
    except AssertionError as e:
        FAIL += 1
        print(f"  FAIL  {name} -- {e}")
    except Exception as e:
        FAIL += 1
        print(f"  ERR   {name} -- {type(e).__name__}: {e}")


def analyze(content, content_type="text", language=None, timeout=90.0):
    body = {"content": content, "content_type": content_type}
    if language:
        body["language"] = language
    resp = httpx.post(f"{API}/analyze", json=body, timeout=timeout)
    assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text[:200]}"
    return resp.json()


# ─── Health ───
def test_health():
    resp = httpx.get(f"{API}/health", timeout=10)
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["qdrant_connected"] is True
    assert len(data["collections"]) == 3


# ─── English: Known misinformation ───
def test_en_upi_ban():
    r = analyze("BREAKING: Government has banned all UPI transactions in India!")
    assert r["detected_language"] == "en"
    assert r["verdict"] in ("false", "misleading")
    assert r["credibility_score"] < 0.6
    assert len(r["claims"]) > 0
    assert len(r["explanation"]) > 50
    assert len(r["counter_content"]) > 20


def test_en_covid_vaccine_microchip():
    r = analyze("COVID-19 vaccines contain microchips for government surveillance")
    assert r["verdict"] in ("false", "misleading", "unverified")
    assert r["credibility_score"] < 0.6
    ext_top = r.get("external_factchecks", [])
    ext_claim = []
    for c in r.get("claims", []):
        ext_claim.extend(c.get("external_factchecks", []))
    all_ext = ext_top + ext_claim
    has_reviews = len(all_ext) > 0
    if has_reviews:
        assert any("false" in fc.get("rating", "").lower() or "fake" in fc.get("rating", "").lower() for fc in all_ext)


def test_en_5g_covid():
    r = analyze("5G towers are spreading COVID-19 through radiation")
    assert r["verdict"] in ("false", "misleading")
    assert len(r.get("external_factchecks", [])) > 0


def test_en_free_laptop_scam():
    r = analyze("PM Modi is giving free laptops to all students via WhatsApp link")
    assert r["verdict"] in ("false", "misleading")


# ─── English: True/neutral content ───
def test_en_true_content():
    r = analyze("ISRO successfully launched Chandrayaan-3 which landed on the Moon's south pole in August 2023.")
    assert r["credibility_score"] > 0.3
    assert r["detected_language"] == "en"


# ─── Hindi ───
def test_hi_5g_conspiracy():
    r = analyze("5G \u091f\u093e\u0935\u0930 COVID-19 \u092b\u0948\u0932\u093e \u0930\u0939\u0947 \u0939\u0948\u0902! \u0938\u0930\u0915\u093e\u0930 \u091b\u0941\u092a\u093e \u0930\u0939\u0940 \u0939\u0948 \u0938\u091a!")
    assert r["detected_language"] == "hi"
    assert r["verdict"] in ("false", "misleading", "unverified")
    assert len(r["explanation"]) > 20


def test_hi_whatsapp_scam():
    r = analyze("WhatsApp \u0932\u093f\u0902\u0915 \u0938\u0947 \u0915\u0947\u0902\u0926\u094d\u0930 \u0938\u0930\u0915\u093e\u0930 \u092e\u0941\u092b\u094d\u0924 \u0932\u0948\u092a\u091f\u0949\u092a \u092c\u093e\u0902\u091f \u0930\u0939\u0940 \u0939\u0948")
    assert r["detected_language"] == "hi"
    assert r["verdict"] in ("false", "misleading", "unverified")


# ─── Tamil ───
def test_ta_vaccine_misinfo():
    r = analyze("COVID-19 \u0ba4\u0b9f\u0bc1\u0baa\u0bcd\u0baa\u0bc2\u0b9a\u0bbf\u0b95\u0bb3\u0bbf\u0bb2\u0bcd \u0bae\u0bc8\u0b95\u0bcd\u0bb0\u0bcb\u0b9a\u0bbf\u0baa\u0bcd\u0b95\u0bb3\u0bcd \u0b89\u0bb3\u0bcd\u0bb3\u0ba9! \u0b85\u0bb0\u0b9a\u0bc1 \u0bae\u0b95\u0bcd\u0b95\u0bb3\u0bc8 \u0b95\u0ba3\u0bcd\u0b95\u0bbe\u0ba3\u0bbf\u0b95\u0bcd\u0b95 \u0ba4\u0bbf\u0b9f\u0bcd\u0b9f\u0bae\u0bbf\u0b9f\u0bc1\u0b95\u0bbf\u0bb1\u0ba4\u0bc1!")
    assert r["detected_language"] == "ta"
    assert r["verdict"] in ("false", "misleading", "unverified")


# ─── Edge cases ───
def test_empty_string():
    r = analyze("   ")
    assert r["verdict"] == "unverified"
    assert r["credibility_score"] == 0.5


def test_single_word():
    r = analyze("hello")
    assert r["detected_language"] == "en"
    assert "verdict" in r


def test_very_long_input():
    long_text = "This is fake news about vaccines being dangerous. " * 200
    r = analyze(long_text)
    assert r["verdict"] in ("false", "misleading", "unverified", "true")
    assert len(r["claims"]) > 0


def test_special_characters():
    r = analyze("!@#$%^&*()_+{}|:<>?~`-=[]\\;',./")
    assert "verdict" in r


def test_mixed_language_hinglish():
    r = analyze("Yeh fake news hai bhai, UPI band nahi hua hai, mat mano ye WhatsApp forward ko")
    assert r["detected_language"] in ("en", "hi")
    assert "verdict" in r


def test_emoji_content():
    r = analyze("BREAKING NEWS 5G causes corona virus! Share this now!")
    assert r["verdict"] in ("false", "misleading", "unverified")


def test_url_numbers_only():
    r = analyze("12345678901234567890")
    assert "verdict" in r


# ─── Credibility breakdown validation ───
def test_breakdown_fields():
    r = analyze("Government banned UPI")
    b = r["breakdown"]
    for field in ["ai_generation_score", "fact_evidence_score", "source_credibility_score",
                  "misinfo_pattern_score", "emotional_language_score", "google_factcheck_score"]:
        assert field in b, f"Missing field: {field}"
        assert 0.0 <= b[field] <= 1.0, f"{field} out of range: {b[field]}"


def test_shareable_summary_nonempty():
    r = analyze("5G towers cause COVID")
    assert len(r["shareable_summary"]) > 10


# ─── Google Fact Check specific ───
def test_google_factcheck_found():
    r = analyze("covid vaccine causes death")
    ext = r.get("external_factchecks", [])
    if ext:
        fc = ext[0]
        assert "publisher_name" in fc
        assert "rating" in fc
        assert "url" in fc


# ─── Image edge case ───
def test_invalid_image():
    r = analyze("not-a-valid-base64-image", content_type="image")
    assert "verdict" in r


def test_tiny_image():
    from PIL import Image
    import io
    img = Image.new("RGB", (2, 2), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    r = analyze(b64, content_type="image")
    assert "verdict" in r
    assert r.get("image_analysis") is not None


if __name__ == "__main__":
    print("\n=== SatyaNet-AI End-to-End Tests ===\n")

    print("[Health]")
    test("health check", test_health)

    print("\n[English - Misinformation]")
    test("UPI ban hoax", test_en_upi_ban)
    test("COVID vaccine microchip", test_en_covid_vaccine_microchip)
    test("5G COVID conspiracy", test_en_5g_covid)
    test("Free laptop scam", test_en_free_laptop_scam)

    print("\n[English - True content]")
    test("ISRO Chandrayaan (true)", test_en_true_content)

    print("\n[Hindi]")
    test("Hindi 5G conspiracy", test_hi_5g_conspiracy)
    test("Hindi WhatsApp scam", test_hi_whatsapp_scam)

    print("\n[Tamil]")
    test("Tamil vaccine misinfo", test_ta_vaccine_misinfo)

    print("\n[Edge Cases]")
    test("empty string", test_empty_string)
    test("single word", test_single_word)
    test("very long input", test_very_long_input)
    test("special characters", test_special_characters)
    test("mixed Hinglish", test_mixed_language_hinglish)
    test("emoji content", test_emoji_content)
    test("numbers only", test_url_numbers_only)

    print("\n[Schema Validation]")
    test("breakdown fields complete", test_breakdown_fields)
    test("shareable summary nonempty", test_shareable_summary_nonempty)

    print("\n[Google Fact Check]")
    test("Google FC returns results", test_google_factcheck_found)

    print("\n[Image]")
    test("invalid image graceful", test_invalid_image)
    test("tiny 2x2 image", test_tiny_image)

    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
    print(f"{'='*50}\n")

    sys.exit(1 if FAIL > 0 else 0)
