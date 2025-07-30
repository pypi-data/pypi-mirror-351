from abc import ABC, abstractmethod
from typing import Any, Dict

class IClient(ABC):
    @abstractmethod
    async def query(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def sign_transaction(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def send_transaction(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def get_transaction(self, *args, **kwargs) -> Any:
        pass 