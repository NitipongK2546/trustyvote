import base64
import json
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature

from django.core.serializers import deserialize

from dotenv import load_dotenv

import logging
import sys

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s %(levelname)s %(message)s'
)

load_dotenv()

# Generate this key once and store it safely
FERNET_KEY = os.getenv('FERNET_KEY') # load from env var ideally
cipher = Fernet(FERNET_KEY)

def encrypt_private_key(private_key_pem: str) -> bytes:
    return cipher.encrypt(private_key_pem)

def decrypt_private_key(encrypted_data: bytes) -> str:
    return cipher.decrypt(encrypted_data).decode()

def create_voting_packet(vote_data, voter_id, voter_public_key_pem, voter_private_key, server_public_key_pem):
    encrypted_vote, aes_key = encrypt_vote(vote_data)

    enc_aes_key = encrypt_aes_key(aes_key, server_public_key_pem)
    
    # Sign vote + AES key + voter_id
    signature = sign_vote(voter_private_key, encrypted_vote, enc_aes_key, voter_id)

    packet = {
        "encrypted_vote": base64.b64encode(encrypted_vote).decode(),    # Encrypt with AES, decrypt with AES key
        "enc_aes_key": base64.b64encode(enc_aes_key).decode(),          # Encrypt with server Kpub, server decrypt with Kpriv
        "voter_id": voter_id,                                           # ID
        "voter_public_key": voter_public_key_pem.decode(),              # Voter public key to verify signature
        "signature": base64.b64encode(signature).decode()               # signature for the first 3 data.
    }
    return packet

# Step 1: Generate AES key and encrypt vote
def encrypt_vote(vote_data: dict):
    aes_key = Fernet.generate_key()
    cipher = Fernet(aes_key)
    
    # Serialize vote data to JSON and encrypt it
    vote_json = json.dumps(vote_data).encode()
    encrypted_vote = cipher.encrypt(vote_json)
    
    return encrypted_vote, aes_key

# Step 2: Encrypt AES key with voter's public RSA key
def encrypt_aes_key(aes_key: bytes, server_public_key_pem: bytes):
    public_key = serialization.load_pem_public_key(server_public_key_pem)
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key

# Step 3: Sign the encrypted_vote (optional but common in voting)
def sign_vote(private_key, encrypted_vote: bytes, enc_aes_key: bytes, voter_id: str):
    # Combine all parts into a single bytes blob
    combined = encrypted_vote + enc_aes_key + voter_id.encode()

    # Sign the combined data
    signature = private_key.sign(
        combined,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(public_key, encrypted_vote, enc_aes_key, voter_id, signature):
    combined = encrypted_vote + enc_aes_key + voter_id.encode()

    try:
        public_key.verify(
            signature,
            combined,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False



def verify_and_decrypt_voting_packet(packet, server_private_key):
    try:
        # Decode base64 fields
        encrypted_vote = base64.b64decode(packet["encrypted_vote"])
        enc_aes_key = base64.b64decode(packet["enc_aes_key"])
        signature = base64.b64decode(packet["signature"])
        voter_id = packet["voter_id"].encode()
        voter_public_key_pem = packet["voter_public_key"].encode()

        # Load voter's public key
        public_key = serialization.load_pem_public_key(voter_public_key_pem)

        # Combine for signature verification
        combined = encrypted_vote + enc_aes_key + voter_id

        # Verify signature
        public_key.verify(
            signature,
            combined,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        print("✅ Signature is valid.")

        # Decrypt AES key using voter's private key
        aes_key = server_private_key.decrypt(
            enc_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Use AES key to decrypt vote
        fernet = Fernet(aes_key)
        decrypted_vote_json = fernet.decrypt(encrypted_vote)
        decrypted_vote = json.loads(decrypted_vote_json)

        # print("\n📝 Entire Voting Packet:")
        # print(json.dumps({
        #     # "encrypted_vote": base64.b64encode(encrypted_vote).decode(),
        #     # "enc_aes_key": base64.b64encode(enc_aes_key).decode(),
        #     # "voter_id": packet["voter_id"],
        #     # "voter_public_key": packet["voter_public_key"],
        #     # "signature": base64.b64encode(signature).decode(),
        #     "decrypted_vote": decrypted_vote
        # }, indent=2))

        print("")
        print("")
        print("")

        check = {
            "enc_aes_key": base64.b64encode(enc_aes_key).decode(),
            "voter_id": packet["voter_id"],
            "voter_public_key": packet["voter_public_key"],
            "signature": base64.b64encode(signature).decode(),
            "decrypted_vote": decrypted_vote
        }

        # print(decrypted_vote)
        logging.info(f"--------------------------------------------------------")

        for key, val in check.items():
            # print(f"{key}: {val}")
            logging.info(f"{key}: {val}")
            logging.info("")


        choice_json = json.loads(decrypted_vote['choice']) 

        choice_json_str = json.dumps(choice_json)

        candidate = list(deserialize('json', choice_json_str))[0].object

        candidate.votes += 1
        candidate.save()

    except InvalidSignature:
        print("❌ Invalid signature! Data may be tampered with.")
    except Exception as e:
        print("❌ Error:", str(e))




# seed = 'your-secret-seed'
# voter_id = 'VOTER12345'
# hmac_hash = create_seeded_hash(voter_id, seed)

############################################################################################
#
# 1. Run code to generate RSA key for voter, voter get var for Kpriv, server get Kpub
# 2. pem public key format for safety
# 3. create a packet of (vote_data, voter_id, voter_public_key_pem, voter_private_key)
# 4. To check the vote, server run verify function.
#
##########################################################################################

# from cryptography.hazmat.primitives.asymmetric import rsa

# voter_private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
# voter_public_key = voter_private_key.public_key()

# # Generate RSA key pair for voter
# voter_private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
# voter_public_key = voter_private_key.public_key()

# # voter_private_key_pem = voter_private_key.private_bytes(
# #         encoding=serialization.Encoding.PEM,
# #         format=serialization.PrivateFormat.PKCS8,
# #         encryption_algorithm=serialization.NoEncryption()
# #     )

# # PEM format


# voter_public_key_pem = voter_public_key.public_bytes(
# encoding=serialization.Encoding.PEM,
# format=serialization.PublicFormat.SubjectPublicKeyInfo
# )

# server_public_key_pem = voter_public_key.public_bytes(
# encoding=serialization.Encoding.PEM,
# format=serialization.PublicFormat.SubjectPublicKeyInfo
# )

# vote_data = {
# "choice": "Alice"
# }
# voter_id = "voter123"

# packet = create_voting_packet(vote_data, voter_id, voter_public_key_pem, voter_private_key, server_public_key_pem)
# # Object.create.object(data=packet)

# verify_and_decrypt_voting_packet(packet, voter_private_key)

# fake_packet = packet.copy()
# fake_packet["signature"] = "FQd2GoACyjKmii++6TQNe34k0xPQSk45RcftNAzMjfXdL4n6vzNWhCF" \
# "BWXZ8n5+BZ7PRyqvAdu1ciyWMDL10rD+EvQyevPDbRpi/y/IZ5QTERe3aRsw6Vjo4cYjvO9FU/cC4rTgoreFw" \
# "8EStQqv7d1v5hVDsHOTS1KBeLM2vmKbOoIPomCIYcAwMOIlH5h3WmpHfYU4himop43aAoOazncmjEpXBJYfDrBEa" \
# "mH9j0PnMO1MaZUSQ9axwMCdq8VNIADFF3ayzc4v6PqdM266gVEkhe2+qsLqkjnCXbt4PkLRAMhmCCScJUc7RspopILa3m" \
# "kVlsApEWKJSjYIibrd0uw=="  # Alter signature to simulate a fake one

# # Step 2: Test with the fake signature (this should fail the verification).
# verify_and_decrypt_voting_packet(fake_packet, voter_private_key)