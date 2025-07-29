from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseHandler(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def register(self, dispatcher: Any):
        """Register handler with the appropriate dispatcher"""
        pass

    @abstractmethod
    async def handle(self, *args, **kwargs):
        """Handle the incoming update"""
        pass
