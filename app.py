from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import base64
import pyotp
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

app = FastAPI()

PRIVATE_KEY_PATH = "student_private.pem"
SEED_FILE_PATH = "data/seed.txt"

# -----------------------------
# MODELS
# -----------------------------
class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# -----------------------------
# ENDPOINT 1: POST /decrypt-seed
# -----------------------------
@app.post("/decrypt-seed")
def decrypt_seed(req: DecryptRequest):
    encrypted_b64 = req.encrypted_seed.strip()

    # Load private key
    if not os.path.exists(PRIVATE_KEY_PATH):
        raise HTTPException(status_code=500, detail="Private key missing")

    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    try:
        ciphertext = base64.b64decode(encrypted_b64)

        # RSA-OAEP SHA256 decryption
        decrypted_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        seed_hex = decrypted_bytes.hex()

        # Validate length
        if len(seed_hex) != 64:
            raise ValueError("Invalid seed length")

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save seed
        with open(SEED_FILE_PATH, "w") as f:
            f.write(seed_hex)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -----------------------------
# ENDPOINT 2: GET /generate-2fa
# -----------------------------
@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not found")

    with open(SEED_FILE_PATH, "r") as f:
        seed_hex = f.read().strip()

    seed_bytes = bytes.fromhex(seed_hex)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    code = totp.now()

    # Calculate remaining time in 30-sec window
    import time
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}

# -----------------------------
# ENDPOINT 3: POST /verify-2fa
# -----------------------------
@app.post("/verify-2fa")
def verify_2fa(req: VerifyRequest):
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not found")

    if not req.code or len(req.code) != 6:
        raise HTTPException(status_code=400, detail="Invalid code")

    with open(SEED_FILE_PATH, "r") as f:
        seed_hex = f.read().strip()

    seed_bytes = bytes.fromhex(seed_hex)
    base32_seed = base64.b32encode(seed_bytes).decode()

    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)

    is_valid = totp.verify(req.code, valid_window=1)

    return {"valid": is_valid}
