class BlockchainUrlUndefinedException(Exception):
    def __init__(self, blockchain_id: str):
        super().__init__(f"Cannot find nodes hosting the blockchain with ID {blockchain_id}")

class MissingBlockchainIdentifierError(Exception):
    def __init__(self):
        super().__init__("Missing blockchain identifier. Please provide either blockchain_rid or blockchain_iid") 

class NumberOfSignersAndSignaturesException(Exception):
    def __init__(self):
        super().__init__("Number of signers and signatures must match")

class GetTransactionRidException(Exception):
    def __init__(self):
        super().__init__("Failed to get transaction rid")

class SignerByteLengthException(Exception):
    def __init__(self):
        super().__init__("Signer must be 32 bytes")

class SignatureByteLengthException(Exception):
    def __init__(self):
        super().__init__("Signature must be 64 bytes")

class DirectoryNodeUrlPoolException(Exception):
    """Raised when directory node URL pool is empty or invalid"""
    pass
