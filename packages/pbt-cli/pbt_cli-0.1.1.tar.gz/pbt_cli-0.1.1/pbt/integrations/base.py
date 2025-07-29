"""Base Integration interface for all PBT integrations"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union


class BaseIntegration(ABC):
    """Base class for all PBT integrations"""
    
    def __init__(self):
        self.configured = False
        self.config = {}
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the integration with necessary credentials and settings"""
        pass
    
    @abstractmethod
    async def validate(self) -> bool:
        """Validate that the integration is properly configured and working"""
        pass
    
    async def connect(self) -> bool:
        """Establish connection to the service"""
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from the service"""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the integration"""
        return {
            "configured": self.configured,
            "connected": False,
            "error": None
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this integration provides"""
        return []