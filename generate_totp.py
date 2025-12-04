import pyotp
import base64

SEED_FILE = "data/seed.txt"

def load_seed_hex():
    with open(SEED_FILE, "r") as f:
        return f.read().strip()

def hex_to_base32(hex_string):
    # convert hex → bytes
    seed_bytes = bytes.fromhex(hex_string)

    # convert bytes → base32 (TOTP requirement)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')

    return base32_seed

def generate_totp():
    print("1. Reading hex seed...")
    hex_seed = load_seed_hex()

    print("2. Converting hex → base32...")
    base32_seed = hex_to_base32(hex_seed)
    print("Base32 Seed:", base32_seed)

    print("3. Generating TOTP code...")
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    code = totp.now()

    print("\n✅ Your current TOTP code:", code)

if __name__ == "__main__":
    generate_totp()
