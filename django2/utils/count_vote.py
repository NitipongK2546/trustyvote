from .send import serialization
from vote.models import VoteCard, Poll
from utils.encrypt import decrypt_private_key
from cryptography.hazmat.backends import default_backend

from utils.encrypt import verify_and_decrypt_voting_packet


def count_vote(poll_code):
    current_poll = Poll.objects.get(poll_code=poll_code)
    server_private_key = decrypt_private_key(current_poll.private_key)
    pem_data = f"""{server_private_key}"""

    server_private_key = serialization.load_pem_private_key(
        pem_data.encode('utf-8'),
        password=None,
        backend=default_backend()
    )

    packets = VoteCard.objects.filter(poll=current_poll)

    print(packets)

    for packet in packets:
        print(packet)
        verify_and_decrypt_voting_packet(packet, server_private_key)
        packet.delete()

#     fake_packet = packet.copy()
#     fake_packet["signature"] = "FQd2GoACyjKmii++6TQNe34k0xPQSk45RcftNAzMjfXdL4n6vzNWhCF" \
#     "BWXZ8n5+BZ7PRyqvAdu1ciyWMDL10rD+EvQyevPDbRpi/y/IZ5QTERe3aRsw6Vjo4cYjvO9FU/cC4rTgoreFw" \
#     "8EStQqv7d1v5hVDsHOTS1KBeLM2vmKbOoIPomCIYcAwMOIlH5h3WmpHfYU4himop43aAoOazncmjEpXBJYfDrBEa" \
#     "mH9j0PnMO1MaZUSQ9axwMCdq8VNIADFF3ayzc4v6PqdM266gVEkhe2+qsLqkjnCXbt4PkLRAMhmCCScJUc7RspopILa3m" \
#     "kVlsApEWKJSjYIibrd0uw=="  # Alter signature to simulate a fake one

# # # Step 2: Test with the fake signature (this should fail the verification).
#     verify_and_decrypt_voting_packet(fake_packet, server_private_key)