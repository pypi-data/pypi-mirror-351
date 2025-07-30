from typing import List, Optional, Union, Dict, Any, Tuple
from dataclasses import dataclass

from .types import GTX, Operation
from ..utils.gtv import GTV, encode_value, decode_value, gtv_auto
from ..utils.gtv_hash import gtv_hash
from cryptography.hazmat.primitives.serialization import load_der_public_key, Encoding, PublicFormat, load_der_private_key
from ..utils.logger import logger
RawGtv = Union[None, bool, bytes, str, int, Dict[str, Any], List[Any]]
RawGtxOp = Tuple[str, List[RawGtv]]
RawGtxBody = Tuple[bytes, List[RawGtxOp], List[bytes]]

def empty_gtx(blockchain_rid: bytes) -> GTX:
    """Create an empty GTX transaction"""
    return GTX(
        blockchain_rid=blockchain_rid,
        operations=[],
        signers=[]
    )

def add_transaction_to_gtx(op_name: str, args: List[Any], gtx: GTX) -> GTX:
    """Add an operation to GTX"""
    if gtx is None:
        raise ValueError("Missing GTX")
    if gtx.signatures:
        raise ValueError("Cannot add operation to already signed transaction")
        
    gtx.operations.append(Operation(op_name=op_name, args=args))
    return gtx

def add_signer_to_gtx(signer: bytes, gtx: GTX) -> None:
    # Convert DER public key to compressed format if needed
    if signer.startswith(b'0V0\x10'):  # DER format header
        key = load_der_public_key(signer)
        signer = key.public_bytes(
            encoding=Encoding.X962,
            format=PublicFormat.CompressedPoint
        )
    gtx.signers.append(signer)

def gtx_to_raw_gtx_body(gtx: GTX) -> RawGtxBody:
    """Convert GTX to raw format for signing"""
    return [
        gtx.blockchain_rid,
        [[op.op_name, op.args or []] for op in gtx.operations],
        gtx.signers
    ]

def gtx_to_raw_gtx(gtx: GTX) -> List:
    """Convert GTX to raw format for serialization"""
    return [
        [
            gtx.blockchain_rid,
            [[op.op_name, op.args] for op in gtx.operations],
            gtx.signers
        ],
        gtx.signatures or []
    ]

def get_digest(gtx: GTX) -> bytes:
    """Get transaction hash"""
    return gtv_hash(gtx_to_raw_gtx(gtx))

def get_digest_to_sign(gtx: GTX) -> bytes:
    """Get digest for signing"""
    raw_gtx_body = gtx_to_raw_gtx_body(gtx)
    return gtv_hash(raw_gtx_body)

def get_digest_to_sign_from_raw_gtx_body(gtx_body: List) -> bytes:
    """Get digest from raw GTX body"""
    return gtv_hash(gtx_body)

def add_signature(public_key: bytes, signature: bytes, gtx: GTX) -> GTX:
    """Add signature to GTX"""
    try:
        # Initialize signatures array if None
        if gtx.signatures is None:
            gtx.signatures = [None] * len(gtx.signers)
        # Extend signatures array if it's shorter than signers
            
        # Find signer index
        try:
            signer_index = gtx.signers.index(public_key)
            while len(gtx.signatures) < signer_index + 1:
                gtx.signatures.append(None)
        except ValueError:
            raise ValueError("Signer not found in GTX")
            
        # Add signature at correct index
        gtx.signatures[signer_index] = signature
        
        logger.debug(f"Added signature at index {signer_index}")
        logger.debug(f"Current signers: {[s.hex() for s in gtx.signers]}")
        logger.debug(f"Current signatures: {[s.hex() if s else None for s in gtx.signatures]}")
        
        return gtx
        
    except Exception as e:
        logger.error(f"Failed to add signature: {str(e)}")
        raise

def serialize(gtx: GTX) -> bytes:
    if gtx.signatures is None:
        gtx.signatures = []
    return encode_value([gtx_to_raw_gtx_body(gtx), gtx.signatures])

def deserialize_gtx(gtx_bytes: bytes) -> GTX:
    """Deserialize GTX from bytes"""
    
    raw_gtx = decode_value(gtx_bytes)
    body = raw_gtx.value[0].value
    signatures = raw_gtx.value[1].value
    
    # Convert blockchain_rid bytes to hex string
    blockchain_rid_bytes = body[0].value
    blockchain_rid = blockchain_rid_bytes.hex().upper()
    
    return GTX(
        blockchain_rid=blockchain_rid,  # Now passing hex string instead of bytes
        operations=[
            Operation(
                op_name=op.value[0].value,
                args=[arg.value for arg in op.value[1].value]
            ) for op in body[1].value
        ],
        signers=[s.value for s in body[2].value],
        signatures=[s.value for s in signatures]
    )

def decode_gtx(tx_bytes: bytes) -> Tuple[List[Any], List[bytes]]:
    """Decode a GTX transaction.
    
    Args:
        tx_bytes: Encoded transaction bytes
    Returns:
        Tuple of (transaction data, signatures)
    """
    decoded = decode_value(tx_bytes)
    if not isinstance(decoded, list) or len(decoded) != 2:
        raise ValueError("Invalid GTX transaction format")

    tx_data, signatures = decoded
    
    if not isinstance(tx_data, list) or len(tx_data) != 3:
        raise ValueError("Invalid GTX transaction data format")

    return tx_data, signatures

def get_transaction_rid_from_serialized_gtx(gtx_bytes: bytes) -> bytes:
    """Get transaction rid from serialized GTX"""
    decoded = decode_value(gtx_bytes)
    
    # Get the body from the decoded array (first element)
    raw_body = decoded.value[0]
    
    # Return bytes directly instead of hex string
    tx_rid = gtv_hash(raw_body)
    return tx_rid

def check_gtx_signatures(tx_hash: bytes, gtx: GTX) -> bool:
    """Verify all signatures in GTX"""
    from .crypto import verify_signature
    
    for i, signer in enumerate(gtx.signers):
        if not verify_signature(tx_hash, signer, gtx.signatures[i]):
            return False
    return True

def check_existing_gtx_signatures(tx_hash: bytes, gtx: GTX) -> bool:
    """Verify only existing signatures in GTX"""
    from .crypto import verify_signature
    
    for i, signer in enumerate(gtx.signers):
        if gtx.signatures[i] and not verify_signature(tx_hash, signer, gtx.signatures[i]):
            return False
    return True 