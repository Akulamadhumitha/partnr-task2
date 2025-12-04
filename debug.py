import json

with open("student_public.pem", "r") as f:
    pk = f.read()

formatted_pk = pk.strip().replace("\n", "\\n")

payload = {
    "student_id": "23A91A0502",
    "github_repo_url": "https://github.com/Akulamadhumitha/partnr-task2",
    "public_key": formatted_pk
}

print("\n===== PAYLOAD YOU ARE SENDING =====\n")
print(json.dumps(payload, indent=4))
