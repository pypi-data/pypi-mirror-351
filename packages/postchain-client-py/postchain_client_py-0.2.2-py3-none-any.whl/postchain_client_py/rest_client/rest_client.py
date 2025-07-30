import asyncio
from ctypes import Union
from typing import Optional, Dict, Any
from dataclasses import dataclass
import aiohttp
import logging
from ..blockchain_client.enums import Method

logger = logging.getLogger(__name__)

@dataclass
class Response:
    status_code: int = 404  # Default to error status code
    body: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None

    @classmethod
    def error_response(cls, error: Exception) -> 'Response':
        """Create an error response"""
        return cls(
            status_code=500,
            body=None,
            error=error
        )

class RestClient:
    def __init__(self, config):
        self.config = config
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def request_with_failover(
        self,
        method: Method,
        endpoint: str,
        data: Any = None,
        headers: Dict[str, str] = None
    ) -> Response:
        """Make request with failover strategy"""
        for endpoint_url in self.config.node_urls:
            for attempt in range(self.config.attempts_per_endpoint):
                try:
                    response = await self._make_request(
                        method,
                        f"{endpoint_url}/{endpoint}",
                        data,
                        headers
                    )
                    logger.debug("Response on failover attempt: %s", response)
                    if response.status_code == 200:
                        if isinstance(response.body, dict):
                            if 'status' in response.body:
                                if response.body['status'] == 'unknown':
                                    logger.debug("Transaction unknown, retrying...")
                                    await asyncio.sleep(self.config.attempt_interval / 1000)
                                    continue
                        return response
                    else:
                        # Return the response as is, without wrapping in an error
                        return response
                except Exception as e:
                    logger.warning(f"Request failed: {str(e)}")
                    if attempt == self.config.attempts_per_endpoint - 1:
                        logger.error("All attempts failed: %s", e)
                        return Response.error_response(e)
        
        return Response.error_response(Exception("All attempts failed"))

    async def _make_request(
        self,
        method: Method,
        url: str,
        data: Any = None,
        headers: Dict[str, str] = None
    ) -> Response:
        """Make a single request"""
        session = await self._get_session()
        headers = {**(headers or {})}

        try:
            async with session.request(
                method.value,
                url,
                data=data if isinstance(data, bytes) else None,
                json=None if isinstance(data, bytes) else data,
                headers=headers,
                ssl=True if url.startswith('https://') else False,
            ) as response:
                content_type = response.headers.get('content-type', '')
                
                if content_type == 'application/octet-stream':
                    response_data = await response.read()
                    # Keep it as bytes, let the blockchain client decode it
                    body = response_data
                elif content_type == 'application/json':
                    body = await response.json()
                else:
                    # For text/plain or any other content type
                    body = await response.text()
                    if not body:
                        body = response.reason
                
                logger.debug("Response data: %s", body)
                await self.close()
                return Response(
                    status_code=response.status,
                    body=body
                )
        except Exception as e:
            await self.close()
            return Response.error_response(e)

    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close() 