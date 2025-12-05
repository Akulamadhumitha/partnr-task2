#!/usr/bin/env python3

import os
import base64
import pyotp
from datetime import datetime, timezone

SEED_FILE = "/data/seed.txt"

def read_seed():
    """Read hexadecimal seed from persistent storage."""
    try:
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
            return hex_seed
    except FileNotFoundError:
        return None

def hex_to_base32(hex_seed):
    """Convert hex seed to base32 for TOTP."""
    raw = bytes.fromhex(hex_seed)
    return base64.b32encode(raw).decode("utf-8")

def generate_totp(hex_seed):
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed)
    return totp.now()

def main():
    seed_hex = read_seed()
    if not seed_hex:
        print("Seed not found.")
        return

    code = generate_totp(seed_hex)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    print(f"{timestamp} - 2FA Code: {code}")

if __name__ == "__main__":
    main()
