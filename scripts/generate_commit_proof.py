import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

# ----- Step 1: Use commit hash directly -----
commit_hash = "cd30d3f489e1eda0709d6f2ac4ef071771e25a46"  # Your 40-character commit hash
print("Commit Hash:", commit_hash)

# ----- Step 2: Load student private key -----
with open('/app/student_private.pem', 'rb') as f:
    private_key = load_pem_private_key(f.read(), password=None)

# ----- Step 3: Sign commit hash with RSA-PSS-SHA256 -----
signature = private_key.sign(
    commit_hash.encode('utf-8'),  # Sign ASCII string of commit hash
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# ----- Step 4: Load instructor public key -----
with open('/app/instructor_public.pem', 'rb') as f:
    public_key = load_pem_public_key(f.read())

# ----- Step 5: Encrypt signature with instructor public key using OAEP-SHA256 -----
encrypted_signature = public_key.encrypt(
    signature,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# ----- Step 6: Base64 encode the encrypted signature -----
proof_b64 = base64.b64encode(encrypted_signature).decode('utf-8')

# ----- Output -----
print("Encrypted Signature (Base64):", proof_b64)
