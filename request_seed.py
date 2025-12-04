import requests
import json

INSTRUCTOR_API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"
STUDENT_ID = "23A91A0502"
GITHUB_REPO_URL = "https://github.com/Akulamadhumitha/partnr-task2"

PUBLIC_KEY_FILE = "student_public.pem"
OUTPUT_FILE = "encrypted_seed.txt"


def load_public_key(key_path):
    """Loads the student public key exactly as PEM text (no newline changes)."""
    try:
        with open(key_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: Public key file '{key_path}' not found.")
        return None


def request_encrypted_seed():
    print("1. Reading student public key...")
    public_key_pem = load_public_key(PUBLIC_KEY_FILE)

    if not public_key_pem:
        return

    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": GITHUB_REPO_URL,
        "public_key": public_key_pem    # IMPORTANT: no newline replacement!
    }

    headers = {"Content-Type": "application/json"}

    print("2. Sending POST request to API...\n")

    try:
        response = requests.post(
            INSTRUCTOR_API_URL,
            headers=headers,
            json=payload,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()
        status = data.get("status")
        encrypted_seed = data.get("encrypted_seed")

        if status == "success" and encrypted_seed:
            print("✅ SUCCESS! Encrypted seed received.")

            with open(OUTPUT_FILE, "w") as f:
                f.write(encrypted_seed)

            print(f"💾 Encrypted seed saved to '{OUTPUT_FILE}'.")
        else:
            print("❌ API returned unexpected response:")
            print(data)

    except requests.exceptions.RequestException as e:
        print(f"❌ Network or request error: {e}")


if __name__ == "__main__":
    request_encrypted_seed()
