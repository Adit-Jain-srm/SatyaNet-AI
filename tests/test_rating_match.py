import re

_FALSE = re.compile(
    r"\b(?:false|fake|incorrect|wrong|pants on fire|misleading|mostly false"
    r"|not true|fabricated|unproven|debunked|untrue|baseless|unfounded"
    r"|half true|mixture)\b",
    re.IGNORECASE,
)
_TRUE = re.compile(
    r"\b(?:true|correct|accurate|mostly true|verified)\b",
    re.IGNORECASE,
)

tests = [
    ("untrue",             "false"),
    ("unknown",            "neither"),
    ("cannot determine",   "neither"),
    ("no evidence",        "neither"),
    ("mostly true",        "true"),
    ("not true",           "false"),
    ("true",               "true"),
    ("false",              "false"),
    ("FALSE",              "false"),
    ("Mostly False",       "false"),
    ("Pants on Fire",      "false"),
    ("accurate",           "true"),
    ("mixture",            "false"),
    ("half true",          "false"),
    ("unverified claim",   "neither"),
    ("the claim is false", "false"),
    ("verified",           "true"),
    ("",                   "neither"),
    ("baseless",           "false"),
    ("correct",            "true"),
    ("This is incorrect.", "false"),
]

all_pass = True
for rating, expected in tests:
    is_false = bool(_FALSE.search(rating))
    is_true = bool(_TRUE.search(rating)) if not is_false else False
    got = "false" if is_false else ("true" if is_true else "neither")
    status = "PASS" if got == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  {status}  {rating:25s} -> expected={expected:8s} got={got}")

print(f"\nAll passed: {all_pass}")
