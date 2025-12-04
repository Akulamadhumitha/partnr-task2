from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import os

PRIVATE_KEY_FILE = "student_private.pem"
ENCRYPTED_SEED_FILE = "encrypted_seed.txt"
OUTPUT_PATH = "data/seed.txt"   # as required by the task: /data/seed.txt

def decrypt_seed():

    # 1. Load private key
    with open(PRIVATE_KEY_FILE, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    # 2. Read encrypted seed (base64 string)
    with open(ENCRYPTED_SEED_FILE, "r") as f:
        encrypted_b64 = f.read().strip()

    encrypted_bytes = base64.b64decode(encrypted_b64)

    # 3. Decrypt using RSA + OAEP + SHA-256
    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    seed_hex = decrypted.hex()

    print("✅ Decryption successful.")
    print("Decrypted Seed (64-char hex):", seed_hex)
    
    # 4. Save to /data/seed.txt
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(seed_hex)

    print(f"💾 Saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    decrypt_seed()
