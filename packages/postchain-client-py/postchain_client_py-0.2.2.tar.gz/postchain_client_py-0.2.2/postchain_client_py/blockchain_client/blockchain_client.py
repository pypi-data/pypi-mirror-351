import logging
from typing import Dict, Any, Optional, List, Union, Callable
from copy import deepcopy
import asyncio

import aiohttp

from .interfaces import IClient
from .types import (
    NetworkSettings, 
    ClientConfig,
    Operation,
    SignMethod,
    TransactionReceipt,
    Transaction,
    SignedTransaction,
    StatusObject,
    ConfirmationProof,
    QueryObject
)
from .enums import FailoverStrategy, ResponseStatus, ChainConfirmationLevel, AnchoringStatus, Method
from .exceptions import (
    BlockchainUrlUndefinedException,
    MissingBlockchainIdentifierError,
    NumberOfSignersAndSignaturesException,
    GetTransactionRidException,
    DirectoryNodeUrlPoolException
)
from ..rest_client import RestClient
from .transaction import (
    sign_transaction,
    send_transaction
)
from ..utils.formatters import to_buffer, to_query_object, to_string
from ..utils.validation import (
    is_transaction_valid,
    is_tx_rid_valid,
    is_network_setting_valid
)
from ..utils.logger import set_verbose, logger

class BlockchainClient(IClient):
    def __init__(self, config: ClientConfig):
        self.config = config
        self.rest_client = RestClient(config)
        set_verbose(config.verbose)
        logger.debug("BlockchainClient initialized with config: %s", config)

    @classmethod
    async def create(cls, settings: NetworkSettings) -> 'BlockchainClient':
        """Factory method to create a blockchain client"""
        logger.debug("Creating BlockchainClient with settings: %s", settings)
        is_network_setting_valid(settings, throw_on_error=True)
        config = await cls._get_client_config_from_settings(settings)
        return cls(config)

    @staticmethod
    async def _get_client_config_from_settings(settings: NetworkSettings) -> ClientConfig:
        node_urls = await BlockchainClient._get_node_urls_from_settings(settings)
        if not node_urls:
            id_value = settings.blockchain_rid or settings.blockchain_iid or "Unknown"
            raise BlockchainUrlUndefinedException(id_value)
        settings.node_url_pool = node_urls
        blockchain_rid = await BlockchainClient._get_blockchain_rid(settings)
        return ClientConfig(
            node_urls=node_urls,
            blockchain_rid=blockchain_rid,
            status_poll_interval=settings.status_poll_interval or 5000,
            status_poll_count=settings.status_poll_count or 5,
            use_sticky_node=settings.use_sticky_node or False,
            directory_chain_rid=settings.directory_chain_rid,
            failover_strategy=settings.failover_strategy or FailoverStrategy.ABORT_ON_ERROR,
            attempts_per_endpoint=settings.attempts_per_endpoint or 3,
            attempt_interval=settings.attempt_interval or 5000,
            unreachable_duration=settings.unreachable_duration or 30000,
            verbose=settings.verbose,
            merkle_hash_version=settings.merkle_hash_version or 1
        )

    @staticmethod
    async def _get_node_urls_from_settings(settings: NetworkSettings) -> List[str]:
        if settings.directory_node_url_pool:
            # If directory_node_url_pool is provided, use node discovery
            directory_urls = settings.directory_node_url_pool if isinstance(settings.directory_node_url_pool, list) else [settings.directory_node_url_pool]
            if not directory_urls:
                raise DirectoryNodeUrlPoolException()
                
            # Get directory chain RID (IID 0)
            directory_rid = await BlockchainClient._get_directory_chain_rid(settings)
            
            # Create temporary client for directory chain
            directory_client = await get_system_client(directory_urls, directory_rid)
            
            # Get blockchain RID if not provided
            blockchain_rid = settings.blockchain_rid
            if not blockchain_rid and settings.blockchain_iid is not None:
                blockchain_rid = await BlockchainClient._get_blockchain_rid(NetworkSettings(node_url_pool=directory_urls, blockchain_iid=settings.blockchain_iid))
            
            if not blockchain_rid:
                raise MissingBlockchainIdentifierError()
                
            # Query directory chain for node URLs
            try:
                node_urls = await directory_client.query("cm_get_blockchain_api_urls", {"blockchain_rid": to_string(to_buffer(blockchain_rid), 'hex')})
                if not node_urls:
                    raise DirectoryNodeUrlPoolException()
                return node_urls
            except Exception as e:
                logger.error(f"Failed to discover node URLs: {str(e)}")
                raise DirectoryNodeUrlPoolException()
                
        elif isinstance(settings.node_url_pool, str):
            return [settings.node_url_pool]
        elif isinstance(settings.node_url_pool, list):
            return settings.node_url_pool
        return []

    @staticmethod
    async def _get_directory_chain_rid(settings: NetworkSettings) -> str:
        """Get directory chain RID (IID 0)"""
        if settings.directory_chain_rid:
            return settings.directory_chain_rid
            
        # Use first directory node URL to get directory chain RID
        directory_url = settings.directory_node_url_pool[0] if isinstance(settings.directory_node_url_pool, list) else settings.directory_node_url_pool
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{directory_url}/brid/iid_0") as response:
                brid = await response.text()
                logger.debug("Directory chain RID response: %s", brid)
                return brid

    @staticmethod
    async def _get_blockchain_rid(settings: NetworkSettings) -> str:
        if settings.blockchain_rid:
            return settings.blockchain_rid
        elif settings.blockchain_iid is not None:
            logger.debug("No blockchain RID provided. Getting blockchain RID from IID: %s", settings.blockchain_iid)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{settings.node_url_pool[0]}/brid/iid_{settings.blockchain_iid}") as response:
                    brid = await response.text()
                    logger.debug("Blockchain RID response from iid: %s", brid)
                    return brid
        raise MissingBlockchainIdentifierError()

    async def query(self, name_or_query_object: Union[str, Dict, QueryObject], args: Dict = None, 
                   callback: Callable = None) -> Any:
        """Execute a query on the blockchain"""
        logger.debug("Executing query - name/object: %s, args: %s", name_or_query_object, args)

        # Construct query object based on input type
        query_object = to_query_object(name_or_query_object, args)

        # Set headers for GTV format
        headers = {
            'Accept': 'application/octet-stream',
            'Content-Type': 'application/octet-stream'
        }

        response = await self.rest_client.request_with_failover(
            Method.POST,
            f"query_gtv/{self.config.blockchain_rid}",
            data=query_object,
            headers=headers
        )

        logger.debug("Query response - status: %s, body: %s", response.status_code, response.body)
        
        # Handle error responses
        if response.status_code == 400 or response.status_code == 404:
            from ..utils.gtv import decode_raw_value
            try:
                if isinstance(response.body, bytes):
                    # Try to decode GTV error message
                    error_message = decode_raw_value(response.body)
                    logger.info("Error message is here: %s", error_message)
                    if isinstance(error_message, str):
                        raise Exception(error_message)
                    elif isinstance(error_message, dict) and 'error' in error_message:
                        raise Exception(error_message['error'])
                    else:
                        # Try to decode as UTF-8 string if GTV decoding fails
                        try:
                            error_text = response.body.decode('utf-8')
                            # Find the actual error message after any binary prefix
                            logger.info("Error text is here: %s", error_text)
                            raise Exception(error_text)
                        except UnicodeDecodeError:
                            raise Exception(str(response.body))
                else:
                    raise Exception(str(response.body))
            except Exception as e:
                if callback:
                    callback(e, None)
                raise e

        if response.error:
            logger.error("Query failed: %s", response)
            if callback:
                callback(response.error, None)
            raise response.error

        if callback:
            callback(None, response.body)

        # Decode successful GTV responses
        if isinstance(response.body, bytes):
            from ..utils.gtv import decode_raw_value
            try:
                decoded_result = decode_raw_value(response.body)
                logger.debug("Decoded GTV response: %s", decoded_result)
                return decoded_result
            except Exception as e:
                logger.error(f"Failed to decode GTV response: {str(e)}")
                return response.body
            
        return response.body

    async def sign_transaction(
        self,
        transaction: Transaction,
        private_key: bytes
    ) -> Transaction:
        """Sign a transaction with the given private key"""
        try:
            # Use sign_transaction from transaction.py
            signed_tx = await sign_transaction(transaction, private_key, self.config.merkle_hash_version)
            return signed_tx
        except Exception as e:
            logger.error(f"Failed to sign transaction: {str(e)}")
            raise

    async def _poll_transaction_status(self, receipt: TransactionReceipt) -> TransactionReceipt:
        """Poll for transaction status updates"""
        logger.debug("Polling for transaction status...")
        for attempt in range(self.config.status_poll_count):
            await asyncio.sleep(self.config.status_poll_interval / 1000)
            
            status_obj = await self.get_transaction_status(receipt.transaction_rid)
            logger.debug("Poll attempt %s/%s: %s", attempt + 1, self.config.status_poll_count, status_obj.status)
            
            receipt.status = status_obj.status
            receipt.status_code = status_obj.status_code
            receipt.message = status_obj.message
            
            # Handle rejection with error message
            if status_obj.status == ResponseStatus.REJECTED.value:
                error_msg = f"Transaction rejected by Postchain: {status_obj.message}"
                logger.error("Error: %s", error_msg)
                raise Exception(error_msg)
            
            # Exit polling if confirmed
            if status_obj.status == ResponseStatus.CONFIRMED.value:
                return receipt
                
        logger.debug("Final transaction status: %s", receipt.status)
        
        # Handle timeout case
        if receipt.status == ResponseStatus.WAITING:
            error_msg = "Transaction timed out - did not receive confirmation within polling period"
            logger.error("Error: %s", error_msg)
            raise Exception(error_msg)
            
        return receipt

    async def send_transaction(
        self,
        transaction: Transaction,
        do_status_polling: bool = True,
        callback: Callable = None
    ) -> TransactionReceipt:
        """Send a transaction to the blockchain"""
        try:
            is_transaction_valid(transaction, isSigned=True, throw_on_error=True)
            # Use send_transaction from transaction.py
            response = await send_transaction(transaction, self.rest_client)
            
            # Check if we got a proper response or just a transaction ID
            if isinstance(response, tuple) and len(response) >= 2:
                # If response contains status_code and body
                tx_rid, status_code, body = response[0], response[1], response[2] if len(response) > 2 else None
                
                # Create receipt based on response
                receipt = TransactionReceipt(
                    transaction_rid=tx_rid,
                    status=ResponseStatus.REJECTED.value if status_code >= 400 else ResponseStatus.WAITING.value,
                    status_code=status_code,
                    message=str(body) if body else None
                )
            else:
                # Backwards compatibility - if we just got a transaction ID
                tx_rid = response
                receipt = TransactionReceipt(
                    transaction_rid=tx_rid,
                    status=ResponseStatus.WAITING.value,
                    status_code=200
                )
            
            # Only poll for status if requested and transaction wasn't immediately rejected
            if do_status_polling and receipt.status == ResponseStatus.WAITING.value:
                receipt = await self._poll_transaction_status(receipt)
                
            if callback:
                callback(None, receipt)
                
            return receipt
            
        except Exception as error:
            if callback:
                callback(error, None)
            raise error

    async def sign_and_send_transaction(
        self,
        transaction: Transaction,
        private_key: bytes,
        do_status_polling: bool = True
    ) -> TransactionReceipt:
        """Sign and send a transaction"""
        try:
            signed_tx = await self.sign_transaction(transaction, private_key)
            return await self.send_transaction(signed_tx, do_status_polling)
        except Exception as error:
            logger.error(f"Failed to sign and send transaction: {str(error)}")
            raise

    async def get_transaction(self, tx_rid: bytes, callback: Callable = None) -> bytes:
        """Get transaction details by transaction RID"""
        try:
            is_tx_rid_valid(tx_rid, throw_on_error=True)
        except Exception as error:
            if callback:
                callback(error, None)
            raise error

        response = await self.rest_client.request_with_failover(
            Method.GET,
            f"tx/{self.config.blockchain_rid}/{to_string(tx_rid, 'hex')}"
        )

        if callback:
            callback(response.error, 
                    to_buffer(response.body['tx']) if response.status_code == 200 else response.body)

        if response.error:
            raise response.error

        return to_buffer(response.body['tx']) if response.status_code == 200 else response.body

    def add_nop(self, transaction: Transaction) -> Transaction:
        """Add a nop operation to the transaction"""
        _transaction = deepcopy(transaction)
        nop_operation = Operation(
            op_name='nop',
            args=[]
        )
        _transaction.operations = [*_transaction.operations, nop_operation]
        return _transaction

    async def _handle_transaction_confirmations(
        self,
        transaction_rid: bytes,
        confirmation_level: ChainConfirmationLevel,
        callback: Callable = None
    ) -> TransactionReceipt:
        """Handle transaction confirmation process"""
        status_obj = await self.get_transaction_status(transaction_rid)
        
        receipt = TransactionReceipt(
            status=status_obj.status,
            status_code=200,
            transaction_rid=transaction_rid
        )

        if confirmation_level == ChainConfirmationLevel.DAPP:
            return receipt

        if status_obj.status == ResponseStatus.CONFIRMED:
            cluster_anchoring = await self.get_cluster_anchoring_transaction_confirmation(
                transaction_rid
            )
            
            if isinstance(cluster_anchoring, dict):  # If it's an anchoring transaction
                receipt.status = AnchoringStatus.CLUSTER_ANCHORED
                receipt.cluster_anchored_tx = cluster_anchoring

                if confirmation_level == ChainConfirmationLevel.SYSTEM:
                    system_anchoring = await self.get_system_anchoring_transaction_confirmation(
                        cluster_anchoring['txRid']
                    )
                    if system_anchoring:
                        receipt.status = AnchoringStatus.SYSTEM_ANCHORED
                        receipt.system_anchored_tx = system_anchoring

        return receipt

    @staticmethod
    def _is_key_pair(sign_method: Any) -> bool:
        """Check if the sign method is a key pair"""
        return hasattr(sign_method, 'priv_key') and hasattr(sign_method, 'pub_key')

    async def get_transaction_status(self, transaction_rid: bytes, 
                                   callback: Optional[Callable] = None) -> StatusObject:
        """Get the status of a transaction"""
        try:
            is_tx_rid_valid(transaction_rid, throw_on_error=True)
        except Exception as error:
            if callback:
                callback(error, None)
            raise error

        response = await self.rest_client.request_with_failover(
            Method.GET,
            f"tx/{self.config.blockchain_rid}/{transaction_rid.hex()}/status",
            data=None,
            headers={'Accept': 'application/json'}  # Explicitly request JSON response
        )
        logger.debug("Transaction status response: %s", response)

        if callback:
            callback(response.error, 
                    response.body if not response.error else None)

        if response.error:
            raise response.error

        # Handle the response body which could be a JSON string or bytes
        response_body = response.body
        
        # If response is bytes, try to decode it
        if isinstance(response_body, bytes):
            try:
                import json
                response_body = json.loads(response_body.decode('utf-8'))
            except Exception as e:
                logger.error(f"Failed to decode response body: {str(e)}")
                raise ValueError(f"Failed to decode response body: {str(e)}")
        
        # If response is a string, try to parse it as JSON
        if isinstance(response_body, str):
            try:
                import json
                response_body = json.loads(response_body)
            except Exception as e:
                logger.error(f"Failed to parse JSON string: {str(e)}")
                raise ValueError(f"Failed to parse JSON string: {str(e)}")
        
        # Now response_body should be a dictionary
        if not isinstance(response_body, dict):
            raise ValueError(f"Unexpected response format: {response.body}")

        return StatusObject(
            status=response_body.get('status'),
            status_code=response.status_code,
            message=response_body.get('rejectReason')
        )

    async def get_transaction_confirmation_level(
        self,
        transaction_rid: bytes,
        callback: Optional[Callable] = None
    ) -> TransactionReceipt:
        """Get the confirmation level of a transaction"""
        try:
            status_obj = await self.get_transaction_status(transaction_rid)
            
            receipt = TransactionReceipt(
                status=status_obj.status,
                status_code=200,
                transaction_rid=transaction_rid
            )

            if status_obj.status == ResponseStatus.CONFIRMED:
                cluster_anchoring = await self.get_cluster_anchoring_transaction_confirmation(
                    transaction_rid
                )
                
                if isinstance(cluster_anchoring, dict):
                    receipt.status = AnchoringStatus.CLUSTER_ANCHORED
                    receipt.cluster_anchored_tx = cluster_anchoring

                    system_anchoring = await self.get_system_anchoring_transaction_confirmation(
                        cluster_anchoring['tx_rid']
                    )
                    if system_anchoring:
                        receipt.status = AnchoringStatus.SYSTEM_ANCHORED
                        receipt.system_anchored_tx = system_anchoring

            if callback:
                callback(None, receipt)
            return receipt

        except Exception as error:
            if callback:
                callback(error, None)
            raise error

    async def get_cluster_anchoring_transaction_confirmation(
        self,
        transaction_rid: bytes,
        callback: Optional[Callable] = None
    ) -> Union[Dict[str, Any], AnchoringStatus]:
        """Get cluster anchoring transaction confirmation"""
        try:
            is_tx_rid_valid(transaction_rid, throw_on_error=True)
        except Exception as error:
            if callback:
                callback(error, None)
            raise error

        try:
            confirmation_proof = await self.get_confirmation_proof(transaction_rid)
            
            d1_client = await get_system_client(
                self.get_client_node_url_pool(),
                self.config.directory_chain_rid
            )

            anchoring_client = await get_anchoring_client(d1_client, self.config.blockchain_rid)
            
            anchoring_transaction = await get_block_anchoring_transaction(
                self,
                anchoring_client,
                transaction_rid,
                confirmation_proof
            )

            if not anchoring_transaction:
                return AnchoringStatus.NOT_ANCHORED

            return anchoring_transaction

        except Exception as error:
            if callback:
                callback(error, None)
            return AnchoringStatus.FAILED_ANCHORING

    async def get_system_anchoring_transaction_confirmation(
        self,
        anchored_tx_rid: bytes,
        callback: Optional[Callable] = None
    ) -> Optional[Dict[str, Any]]:
        """Get system anchoring transaction confirmation"""
        try:
            is_tx_rid_valid(anchored_tx_rid, throw_on_error=True)
        except Exception as error:
            if callback:
                callback(error, None)
            raise error

        d1_client = await get_system_client(
            self.get_client_node_url_pool(),
            self.config.directory_chain_rid
        )

        system_anchoring_chain_rid = await get_system_anchoring_chain(d1_client)
        
        if not system_anchoring_chain_rid:
            return None

        system_anchoring_chain_client = await get_system_client(
            self.get_client_node_url_pool(),
            system_anchoring_chain_rid.hex()
        )

        anchoring_client = await get_anchoring_client(d1_client, self.config.blockchain_rid)
        anchoring_proof = await anchoring_client.get_confirmation_proof(anchored_tx_rid)
        block_rid = calculate_block_rid(anchoring_proof)

        system_anchoring_transaction = await await_get_anchoring_transaction_for_block_rid(
            system_anchoring_chain_client,
            to_buffer(anchoring_client.config.blockchain_rid),
            block_rid,
            system_anchoring_chain_client.config.status_poll_interval,
            system_anchoring_chain_client.config.status_poll_count
        )

        if not is_valid_anchoring_transaction(system_anchoring_transaction):
            return None

        return system_anchoring_transaction 

    def get_client_node_url_pool(self) -> List[str]:
        """Get the list of node URLs for this client"""
        return self.config.node_urls

async def get_system_client(node_url_pool: List[str], blockchain_rid: str) -> 'BlockchainClient':
    """Create a system client for interacting with system chains"""
    settings = NetworkSettings(
        node_url_pool=node_url_pool,
        blockchain_rid=blockchain_rid
    )
    return await BlockchainClient.create(settings)

async def get_anchoring_client(d1_client: 'BlockchainClient', blockchain_rid: str) -> 'BlockchainClient':
    """Get client for the anchoring chain"""
    try:
        # Query the directory chain to get anchoring chain info
        anchoring_chain_info = await d1_client.query("get_anchoring_chain", {
            "blockchain_rid": blockchain_rid
        })
        
        if not anchoring_chain_info:
            return None
        
        # Create client for the anchoring chain
        return await get_system_client(
            d1_client.get_client_node_url_pool(),
            anchoring_chain_info['blockchain_rid']
        )
    except Exception:
        return None

async def get_block_anchoring_transaction(
    source_client: 'BlockchainClient',
    anchoring_client: 'BlockchainClient',
    transaction_rid: bytes,
    confirmation_proof: Any
) -> Optional[Dict[str, Any]]:
    """Get the anchoring transaction for a specific block"""
    try:
        if not confirmation_proof:
            return None
            
        block_rid = calculate_block_rid(confirmation_proof)
        
        # Query the anchoring chain for the anchoring transaction
        anchoring_tx = await await_get_anchoring_transaction_for_block_rid(
            anchoring_client,
            to_buffer(source_client.config.blockchain_rid),
            block_rid,
            anchoring_client.config.status_poll_interval,
            anchoring_client.config.status_poll_count
        )
        
        return anchoring_tx if is_valid_anchoring_transaction(anchoring_tx) else None
        
    except Exception:
        return None

async def get_system_anchoring_chain(d1_client: 'BlockchainClient') -> Optional[bytes]:
    """Get the system anchoring chain RID"""
    try:
        result = await d1_client.query("get_system_anchoring_chain", {})
        return to_buffer(result['blockchain_rid']) if result else None
    except Exception:
        return None

def calculate_block_rid(confirmation_proof: Any) -> bytes:
    """Calculate block RID from confirmation proof"""
    # Implementation depends on your specific proof format
    # This is a placeholder implementation
    return confirmation_proof.get('blockRid', b'')

async def await_get_anchoring_transaction_for_block_rid(
    client: 'BlockchainClient',
    source_chain_rid: bytes,
    block_rid: bytes,
    poll_interval: int,
    max_polls: int
) -> Optional[Dict[str, Any]]:
    """Poll for anchoring transaction until found or timeout"""
    for _ in range(max_polls):
        try:
            result = await client.query("get_anchoring_tx", {
                "sourceChainRid": to_string(source_chain_rid, 'hex'),
                "blockRid": to_string(block_rid, 'hex')
            })
            
            if result:
                return result
                
            await asyncio.sleep(poll_interval / 1000)  # Convert to seconds
            
        except Exception:
            await asyncio.sleep(poll_interval / 1000)
            
    return None

def is_valid_anchoring_transaction(tx: Optional[Dict[str, Any]]) -> bool:
    """Validate anchoring transaction structure"""
    if not tx:
        return False
        
    required_fields = ['txRid', 'status', 'timestamp']
    return all(field in tx for field in required_fields)