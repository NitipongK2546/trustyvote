from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate RSA keys
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Get the public key from the private key
public_key = private_key.public_key()

# Serialize the private key to PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize the public key to PEM format
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Print the keys
print("Private Key:")
print(private_pem.decode())

print("\nPublic Key:")
print(public_pem.decode())

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# Generate RSA keys
key = RSA.generate(2048)

# Export private and public keys
private_key = key.export_key()
public_key = key.publickey().export_key()

# Print the keys
print("Private Key:")
print(private_key.decode())

print("\nPublic Key:")
print(public_key.decode())
