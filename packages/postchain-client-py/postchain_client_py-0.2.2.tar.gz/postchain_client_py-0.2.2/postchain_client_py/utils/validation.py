from dataclasses import dataclass
from typing import TypeVar, Optional, Dict, Any, Callable

from .logger import logger

from ..blockchain_client.exceptions import NumberOfSignersAndSignaturesException, SignatureByteLengthException, SignerByteLengthException
class ZodError(Exception):
    """Custom validation error class"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

T = TypeVar('T')

@dataclass
class ValidationOptions:
    throw_on_error: bool = False

@dataclass
class ValidationResult:
    success: bool
    error: Optional[ZodError] = None
    message: Optional[str] = None

ValidationFunction = Callable[[Any, Optional[ValidationOptions]], ValidationResult] 
def is_tx_rid_valid(rid: Any, throw_on_error: bool = False) -> ValidationResult:
    """Validate transaction RID"""
    try:
        if not isinstance(rid, bytes) or len(rid) != 32:
            raise ValueError("Transaction RID must be 32 bytes")
        return ValidationResult(success=True)
    except Exception as e:
        if throw_on_error:
            raise
        return ValidationResult(success=False, error=str(e))

def is_sign_method_valid(sign_method: Any, throw_on_error: bool = False) -> ValidationResult:
    """Validate signing method"""
    try:
        if not hasattr(sign_method, 'pub_key'):
            raise ValueError("Sign method must have pub_key")
        if not (hasattr(sign_method, 'priv_key') or hasattr(sign_method, 'sign')):
            raise ValueError("Sign method must have either priv_key or sign method")
        return ValidationResult(success=True)
    except Exception as e:
        if throw_on_error:
            raise
        return ValidationResult(success=False, error=str(e))

def is_network_setting_valid(settings: Any, throw_on_error: bool = False) -> ValidationResult:
    """Validate network settings"""
    try:
        if not (settings.node_url_pool or settings.directory_node_url_pool):
            raise ValueError("Must provide either node_url_pool or directory_node_url_pool")
        if not (settings.blockchain_rid or settings.blockchain_iid is not None):
            raise ValueError("Must provide either blockchain_rid or blockchain_iid")
        return ValidationResult(success=True)
    except Exception as e:
        if throw_on_error:
            raise
        return ValidationResult(success=False, error=str(e))
def is_transaction_valid(transaction: Any, isSigned: bool = False, throw_on_error: bool = False) -> ValidationResult:
    """Validate transaction"""
    try:
        if not transaction.operations:
            raise ValueError("Transaction must have at least one operation")
        if isSigned:
            if not transaction.signers:
                raise ValueError("Transaction must have at least one signer")
            if not transaction.signatures:
                raise ValueError("Transaction must have at least one signature")
            if len(transaction.signers) != len(transaction.signatures):
                raise NumberOfSignersAndSignaturesException
            for i in range(len(transaction.signers)):
                if len(transaction.signers[i]) != 32 and len(transaction.signers[i]) != 33:
                    print("Signer length is %s", len(transaction.signers[i]))
                    raise SignerByteLengthException
                if len(transaction.signatures[i]) != 64:
                    raise SignatureByteLengthException
        return ValidationResult(success=True)
    except Exception as e:
        if throw_on_error:
            raise
        return ValidationResult(success=False, error=str(e))
