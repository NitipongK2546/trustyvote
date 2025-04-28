import secrets
import string
import hmac
import hashlib

def generate_poll_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_seeded_hash(voter_id: str, seed: str) -> str:
    key_bytes = seed.encode('utf-8')
    message_bytes = voter_id.encode('utf-8')

    hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha256)

    return hmac_obj.hexdigest()