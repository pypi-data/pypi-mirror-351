import os
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from dataclasses import dataclass

from .enums import Method
from ..rest_client.rest_client import RestClient
from ..utils.gtv_hash import gtv_hash
from .types import Transaction
from cryptography.hazmat.primitives.asymmetric import ec, utils

from .gtx import GTX, Operation, RawGtxBody, add_signature, get_transaction_rid_from_serialized_gtx, gtx_to_raw_gtx_body, serialize
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from coincurve import PrivateKey
from cryptography.hazmat.primitives import serialization
from ..utils.logger import logger


__all__ = [
    'get_digest_to_sign',
    'sign_transaction',
    'send_transaction'
]
def get_digest_to_sign(transaction: Transaction) -> RawGtxBody:
    """Get the digest that needs to be signed"""
    try:
        # Create GTX object
        gtx = GTX(
            blockchain_rid=transaction.blockchain_rid if isinstance(transaction.blockchain_rid, bytes)
            else bytes.fromhex(transaction.blockchain_rid),
            operations=[Operation(op.name, op.args or []) for op in transaction.operations],
            signers=transaction.signers
        )
        
        # Convert to raw GTX body format
        raw_gtx_body = (
            gtx.blockchain_rid,
            [(op.op_name, op.args) for op in gtx.operations],
            gtx.signers
        )
        
        # Encode to GTV format
        
        # Hash the encoded body
        return raw_gtx_body
        
    except Exception as e:
        raise ValueError(f"Failed to get digest: {e}")

async def sign_transaction(
    transaction: Transaction,
    private_key: bytes,
    merkle_hash_version: int = 1
) -> Transaction:
    """Sign a transaction with the given private key"""
    try:
        priv_key = PrivateKey(private_key)
        public_key = priv_key.public_key.format(True)
        has_op = any(op.op_name == "nop" for op in transaction.operations)
        # Create GTX object
        gtx = GTX(
            blockchain_rid=bytes.fromhex(transaction.blockchain_rid) if isinstance(transaction.blockchain_rid, str)
            else transaction.blockchain_rid,
            operations=[
                Operation(op_name=op.op_name, args=op.args or []) 
                for op in transaction.operations
            ] + ([Operation(op_name="nop", args=[os.urandom(32)])] if transaction.signatures is None and not has_op and merkle_hash_version == 1 else []),  # Add nop operation only if not signed
            signers=transaction.signers,
            signatures=[]
        )

        # Get raw GTX body and sign
        raw_gtx = gtx_to_raw_gtx_body(gtx)
        signature = sign(priv_key, raw_gtx)
        gtx.signatures = transaction.signatures
        # Add signature
        signed_gtx = add_signature(public_key, signature, gtx)
        logger.debug("Signed transaction: %s", signed_gtx)
        logger.debug("Signed transaction signatures: %s", signed_gtx.signatures)
        
        # Convert back to Transaction
        return Transaction(
            operations=signed_gtx.operations,
            signers=signed_gtx.signers,
            signatures=signed_gtx.signatures,
            blockchain_rid=transaction.blockchain_rid
        )
        
    except Exception as e:
        logger.error("Failed to sign transaction: %s", str(e))
        raise

async def send_transaction(
    transaction: Transaction,
    rest_client: RestClient,
) -> tuple:
    """
    Send a signed transaction to the blockchain
    Returns a tuple of (transaction_rid, status_code, body)
    """
    try:
        # Create GTX object
        gtx = GTX(
            blockchain_rid=bytes.fromhex(transaction.blockchain_rid) if isinstance(transaction.blockchain_rid, str)
            else transaction.blockchain_rid,
            operations=transaction.operations,
            signers=transaction.signers,
            signatures=transaction.signatures
        )
        
        # Serialize using GTX serialization
        serialized_tx = serialize(gtx)
        
        # Send via REST client with proper headers
        headers = {
            'Content-Type': 'application/octet-stream',
            'Accept': 'application/octet-stream'
        }
        
        response = await rest_client.request_with_failover(
            Method.POST,
            f"tx/{transaction.blockchain_rid}",
            data=serialized_tx,
            headers=headers
        )
        
        if response.error:
            logger.error("Failed to send transaction: %s", response.error)
            raise response.error
            
        # Return transaction RID, status code, and body
        logger.debug("Transaction sent with response: %s", response)
        tx_rid = get_transaction_rid_from_serialized_gtx(serialized_tx)
        return (tx_rid, response.status_code, response.body)
        
    except Exception as e:
        logger.error("Error sending transaction: %s", str(e))
        raise

def sign_digest_64_der(digest32: bytes, priv_key: PrivateKey) -> bytes:
    """
    Sign a 32-byte digest with coincurve's sign() => DER-encoded signature,
    then decode to r, s, and re-encode as a raw 64-byte array.
    """
    # 1) DER signature => ~70 bytes
    der_signature = priv_key.sign(digest32, hasher=None)

    # 2) Decode DER => r, s (as Python integers)
    r, s = decode_dss_signature(der_signature)

    # 3) Each must be 32 bytes big-endian
    r_bytes = r.to_bytes(32, 'big')
    s_bytes = s.to_bytes(32, 'big')

    # 4) Concatenate => 64 bytes raw
    signature_64 = r_bytes + s_bytes

    return signature_64

def sign(priv_key: PrivateKey, raw_gtx_body: RawGtxBody) -> bytes:
    """Sign a raw GTX body with a private key"""
    # Hash the raw GTX body
    digest = gtv_hash(raw_gtx_body)
    logger.debug(f"Digest to sign: {digest.hex()}")
    
    # Sign the digest
    signature = sign_digest_64_der(digest, priv_key)
    logger.debug(f"Final signature length: {len(signature)}")
    return signature