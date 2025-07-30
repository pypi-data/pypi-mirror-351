from enum import Enum

class FailoverStrategy(Enum):
    ABORT_ON_ERROR = "abortOnError"
    RETRY = "retry"
    QUERY_MAJORITY = "queryMajority"

class ResponseStatus(Enum):
    WAITING = "waiting"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE" 

class ChainConfirmationLevel(Enum):
    CHAIN = "chain"
    CLUSTER = "cluster"
    SYSTEM = "system"
    DAPP = "dapp"

class AnchoringStatus(Enum):
    NOT_ANCHORED = "not_anchored"
    FAILED_ANCHORING = "failed_anchoring"
    CLUSTER_ANCHORED = "cluster_anchored"
    SYSTEM_ANCHORED = "system_anchored"