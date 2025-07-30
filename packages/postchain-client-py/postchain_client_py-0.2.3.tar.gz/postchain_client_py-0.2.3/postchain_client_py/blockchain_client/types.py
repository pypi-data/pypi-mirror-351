from dataclasses import dataclass, field
from typing import Optional, Union, List, Dict, Any

from ..utils.gtv import RawGtv

from .enums import FailoverStrategy, ResponseStatus
from enum import Enum

@dataclass
class NetworkSettings:
    node_url_pool: Optional[List[str]] = None
    directory_node_url_pool: Optional[List[str]] = None
    blockchain_rid: Optional[str] = None
    blockchain_iid: Optional[int] = None
    status_poll_interval: Optional[int] = 500
    status_poll_count: Optional[int] = 5
    use_sticky_node: bool = False
    directory_chain_rid: Optional[str] = None
    verbose: bool = False
    failover_strategy: FailoverStrategy = FailoverStrategy.ABORT_ON_ERROR
    attempts_per_endpoint: int = 3
    attempt_interval: int = 5000
    unreachable_duration: int = 30000
    merkle_hash_version: int = 1

@dataclass
class ClientConfig:
    blockchain_rid: str
    node_urls: List[str]
    status_poll_interval: int = 500
    status_poll_count: int = 5
    failover_strategy: FailoverStrategy = FailoverStrategy.ABORT_ON_ERROR
    attempts_per_endpoint: int = 3
    attempt_interval: int = 5000
    unreachable_duration: int = 30000
    directory_chain_rid: Optional[str] = None
    use_sticky_node: bool = False
    verbose: bool = False
    merkle_hash_version: int = 1

@dataclass
class TransactionReceipt:
    status: str
    status_code: Optional[int]
    transaction_rid: bytes
    message: Optional[str] = None
    cluster_anchored_tx: Optional[Any] = None
    system_anchored_tx: Optional[Any] = None

@dataclass
class Operation:
    """Single blockchain operation"""
    op_name: str
    args: Optional[List[RawGtv]] = None  # Make args optional with default None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op_name": self.op_name,
            "args": self.args
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        return cls(
            op_name=data["op_name"],
            args=data.get("args", [])
        )

@dataclass
class QueryObject:
    """Query object for blockchain queries"""
    name: str
    args: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "args": self.args
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryObject':
        return cls(
            name=data["name"],
            args=data.get("args", {})
        )
    
    def __str__(self) -> str:
        return f"QueryObject(name='{self.name}', args={self.args})"
    
    def __repr__(self) -> str:
        return self.__str__()

@dataclass
class GTX:
    blockchain_rid: bytes
    operations: List[Operation]
    signers: Optional[List[bytes]] = None
    signatures: Optional[List[bytes]] = None

@dataclass
class Transaction:
    """Raw transaction before signing"""
    operations: List[Operation]  # Change from Dict to Operation class
    signers: Optional[List[bytes]] = field(default_factory=list)
    signatures: Optional[List[bytes]] = None
    blockchain_rid: Optional[bytes] = None
    _client_config: Optional['ClientConfig'] = field(default=None, compare=False, repr=False)

    def __post_init__(self):
        """Automatically set blockchain_rid from client config if not provided"""
        if self.blockchain_rid is None and self._client_config is not None:
            if isinstance(self._client_config.blockchain_rid, str):
                self.blockchain_rid = bytes.fromhex(self._client_config.blockchain_rid)
            else:
                self.blockchain_rid = self._client_config.blockchain_rid

    @classmethod
    def create(cls, operations: List[Operation], signers: Optional[List[bytes]] = None, 
               signatures: Optional[List[bytes]] = None, blockchain_rid: Optional[bytes] = None,
               client_config: Optional['ClientConfig'] = None) -> 'Transaction':
        """Create a Transaction with automatic blockchain_rid from client config"""
        return cls(
            operations=operations,
            signers=signers,
            signatures=signatures,
            blockchain_rid=blockchain_rid,
            _client_config=client_config
        )

    def with_config(self, client_config: 'ClientConfig') -> 'Transaction':
        """Return a new Transaction with client config applied"""
        return Transaction.create(
            operations=self.operations,
            signers=self.signers,
            signatures=self.signatures,
            blockchain_rid=self.blockchain_rid,
            client_config=client_config
        )

    @classmethod
    def to_gtx(cls, transaction: 'Transaction') -> GTX:
        return GTX(
            blockchain_rid=transaction.blockchain_rid,
            operations=transaction.operations,
            signers=transaction.signers,
            signatures=transaction.signatures
        )

@dataclass
class SignedTransaction:
    """Transaction after signing"""
    operations: List[Operation]
    signers: List[bytes]
    signatures: List[bytes]

@dataclass
class StatusObject:
    status: str
    status_code: int
    message: Optional[str] = None

class ChainConfirmationLevel(Enum):
    DAPP = "dapp"
    CLUSTER = "cluster"
    SYSTEM = "system"

class AnchoringStatus(Enum):
    NOT_ANCHORED = "not_anchored"
    FAILED_ANCHORING = "failed_anchoring"
    CLUSTER_ANCHORED = "cluster_anchored"
    SYSTEM_ANCHORED = "system_anchored"

class ConfirmationProof:
    pass  # Add appropriate attributes and methods 

@dataclass
class SignMethod:
    """Signing method containing key pair"""
    priv_key: bytes
    pub_key: bytes