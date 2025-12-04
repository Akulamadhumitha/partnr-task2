from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp
import time

app = FastAPI()
DATA_PATH = Path("./data/seed.txt")

# -----------------------------
# Request models
# -----------------------------
class DecryptSeedPayload(BaseModel):
    encrypted_seed: str

class Verify2FAPayload(BaseModel):
    code: str

# -----------------------------
# Endpoint 1: Decrypt Seed
# -----------------------------
@app.post("/decrypt-seed")
def decrypt_seed(payload: DecryptSeedPayload):
    encrypted_seed_b64 = payload.encrypted_seed.strip()
    if not encrypted_seed_b64:
        raise HTTPException(status_code=400, detail="Encrypted seed required")

    # Decode Base64
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Base64")

    # Load private key
    try:
        with open("student_private.pem", "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
    except Exception:
        raise HTTPException(status_code=500, detail="Private key load failed")

    # Decrypt
    try:
        decrypted = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Decryption failed")

    # Decode bytes to string (already hex)
    try:
        seed_hex = decrypted.decode()  # 64-character hex
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decode decrypted seed")

    if len(seed_hex) != 64:
        raise HTTPException(status_code=400, detail="Invalid seed length")

    # Save to file
    DATA_PATH.parent.mkdir(exist_ok=True)
    DATA_PATH.write_text(seed_hex)

    return {"status": "ok"}

# -----------------------------
# Helper: get TOTP from hex seed
# -----------------------------
def totp_from_hex_seed(seed_hex: str) -> pyotp.TOTP:
    seed_bytes = bytes.fromhex(seed_hex)             # hex -> bytes
    seed_b32 = base64.b32encode(seed_bytes).decode() # bytes -> Base32
    return pyotp.TOTP(seed_b32)

# -----------------------------
# Endpoint 2: Generate TOTP
# -----------------------------
@app.get("/generate-2fa")
def generate_2fa():
    if not DATA_PATH.exists():
        raise HTTPException(status_code=400, detail="Seed not found")

    seed_hex = DATA_PATH.read_text().strip()
    totp = totp_from_hex_seed(seed_hex)
    code = totp.now()

    period = totp.interval
    valid_for = period - int(time.time() % period)

    return {"code": code, "valid_for": valid_for}

# -----------------------------
# Endpoint 3: Verify TOTP
# -----------------------------
@app.post("/verify-2fa")
def verify_2fa(payload: Verify2FAPayload):
    code = payload.code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Code required")

    if not DATA_PATH.exists():
        raise HTTPException(status_code=400, detail="Seed not found")

    seed_hex = DATA_PATH.read_text().strip()
    totp = totp_from_hex_seed(seed_hex)

    valid = totp.verify(code, valid_window=1)
    return {"valid": valid}
