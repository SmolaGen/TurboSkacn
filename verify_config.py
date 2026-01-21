import os
import sys
from dotenv import load_dotenv

# Force reload of .env
if os.path.exists("apps/backend/.env"):
    load_dotenv("apps/backend/.env", override=True)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "apps/backend"))

try:
    from phase_config import resolve_model_id
except ImportError:
    print("Error: Could not import phase_config")
    sys.exit(1)

print("-" * 50)
print("CONFIGURATION CHECK")
print("-" * 50)

base_url = os.environ.get("ANTHROPIC_BASE_URL")
print(f"ANTHROPIC_BASE_URL: {base_url}")

if base_url != "http://127.0.0.1:8317/v1":
    print("❌ FAIL: ANTHROPIC_BASE_URL should be http://127.0.0.1:8317/v1")
else:
    print("✅ PASS: ANTHROPIC_BASE_URL is correct")

oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
print(f"CLAUDE_CODE_OAUTH_TOKEN: {oauth_token}")
if oauth_token == "9CDCC8DB-769D-48BD-AF4D-08F97A47BE98":
    print("✅ PASS: Auth Token matches Management Key")
else:
    print("❌ FAIL: Auth Token does not match expected key")

print("\n" + "-" * 50)
print("MODEL RESOLUTION CHECK")
print("-" * 50)

# Test cases
tests = [
    ("claude-haiku-4-5", "gemini-2.5-flash"), # Mapped via ANTHROPIC_DEFAULT_HAIKU_MODEL
    ("claude-3-haiku-20240307", "gemini-2.5-flash"), # Should resolve to default haiku
    ("claude-sonnet-4-5", "gemini-claude-sonnet-4-5"), # Mapped via ANTHROPIC_DEFAULT_SONNET_MODEL
    ("claude-3-5-sonnet-20241022", "gemini-claude-sonnet-4-5"), # Should resolve to default sonnet
    ("opus", "gemini-claude-opus-4-5-thinking"), # Mapped via ANTHROPIC_DEFAULT_OPUS_MODEL
    ("claude-3-opus-20240229", "gemini-claude-opus-4-5-thinking"),
]

all_passed = True
for input_model, expected in tests:
    resolved = resolve_model_id(input_model)
    if resolved == expected:
        print(f"✅ PASS: '{input_model}' -> '{resolved}'")
    else:
        print(f"❌ FAIL: '{input_model}' -> '{resolved}' (Expected: '{expected}')")
        all_passed = False

if all_passed:
    print("\n✅ ALL LOGIC TESTS PASSED")
else:
    print("\n❌ SOME TESTS FAILED")
