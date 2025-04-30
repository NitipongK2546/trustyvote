from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from utils.encrypt import decrypt_private_key

from vote.models import VoteCard, Poll

from utils.encrypt import create_voting_packet, verify_and_decrypt_voting_packet


def send_vote(vote_data, voter_id, server_public_key_pem, poll_code):
    # Generate RSA key pair for voter
    voter_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend)
    voter_public_key = voter_private_key.public_key()

    # voter_private_key_pem = voter_private_key.private_bytes(
    #         encoding=serialization.Encoding.PEM,
    #         format=serialization.PrivateFormat.PKCS8,
    #         encryption_algorithm=serialization.NoEncryption()
    #     )

    # PEM format
    voter_public_key_pem = voter_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # server_public_key_pem = server_public_key.public_bytes(
    #     encoding=serialization.Encoding.PEM,
    #     format=serialization.PublicFormat.SubjectPublicKeyInfo
    # )
    current_poll = Poll.objects.get(poll_code=poll_code)
    packet = create_voting_packet(vote_data, voter_id, voter_public_key_pem, voter_private_key, server_public_key_pem)
    VoteCard.objects.create(data=packet, poll=current_poll)
    print("/n")
    print(packet)

    # current_poll = Poll.objects.get(poll_code=poll_code)
    # server_private_key = decrypt_private_key(current_poll.private_key)
    # pem_data = f"""{server_private_key}"""

    # server_private_key = serialization.load_pem_private_key(
    #     pem_data.encode('utf-8'),
    #     password=None,
    #     backend=default_backend()
    # )

    # # print(server_private_key)

    # # server_public_key = server_public_key.public_bytes(
    # #             encoding=serialization.Encoding.PEM,
    # #             format=serialization.PublicFormat.SubjectPublicKeyInfo
    # #         )

    # verify_and_decrypt_voting_packet(packet, server_private_key)

#     fake_packet = packet.copy()
#     fake_packet["signature"] = "FQd2GoACyjKmii++6TQNe34k0xPQSk45RcftNAzMjfXdL4n6vzNWhCF" \
#     "BWXZ8n5+BZ7PRyqvAdu1ciyWMDL10rD+EvQyevPDbRpi/y/IZ5QTERe3aRsw6Vjo4cYjvO9FU/cC4rTgoreFw" \
#     "8EStQqv7d1v5hVDsHOTS1KBeLM2vmKbOoIPomCIYcAwMOIlH5h3WmpHfYU4himop43aAoOazncmjEpXBJYfDrBEa" \
#     "mH9j0PnMO1MaZUSQ9axwMCdq8VNIADFF3ayzc4v6PqdM266gVEkhe2+qsLqkjnCXbt4PkLRAMhmCCScJUc7RspopILa3m" \
#     "kVlsApEWKJSjYIibrd0uw=="  # Alter signature to simulate a fake one

# # # Step 2: Test with the fake signature (this should fail the verification).
#     verify_and_decrypt_voting_packet(fake_packet, server_private_key)

