from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hashes import SHA256

from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption
from cryptography.hazmat.primitives.asymmetric import dh

def generate_dh_keys():
    """
    Generate Diffie-Hellman keys (private and public) and return them in PEM format.
    """
    # Generate Diffie-Hellman parameters
    parameters = dh.generate_parameters(generator=2, key_size=1024)
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()

    # Serialize private key to PEM format (PKCS8 with no encryption)
    private_key_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,  # Use PKCS8 for private key format
        encryption_algorithm=NoEncryption()  # No encryption for private key
    ).decode('utf-8')

    # Serialize public key to PEM format (SubjectPublicKeyInfo)
    public_key_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # Return the serialized private and public keys as strings
    return private_key_pem, public_key_pem



def derive_shared_key(private_key, peer_public_key):
    shared_key = private_key.exchange(peer_public_key)
    derived_key = HKDF(
        algorithm=SHA256(),
        length=32,
        salt=None,
        info=b'chat'
    ).derive(shared_key)
    return derived_key
