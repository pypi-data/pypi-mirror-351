from coincurve import PublicKey, PrivateKey
from ..utils.gtv_hash import gtv_hash

def verify_signature(
    message: bytes,
    signature: bytes,
    public_key: bytes
) -> bool:
    """
    Verify an ECDSA signature using secp256k1
    """
    try:
        # Create PublicKey instance
        pub_key = PublicKey(public_key)
        
        # Parse the signature
        sig = pub_key.ecdsa_deserialize_compact(signature)
        
        # Verify the signature
        return pub_key.ecdsa_verify(message, sig)
        
    except Exception:
        return False

def create_public_key(private_key: bytes) -> bytes:
    """
    Create public key from private key using secp256k1
    """
    # Create PrivateKey instance
    priv_key = PrivateKey(private_key)
    
    # Get the public key in compressed format
    return priv_key.pubkey.serialize(compressed=True) 