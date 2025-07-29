from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Type, List, Optional, cast
from dataclasses import dataclass

T = TypeVar('T', bound='BaseDTO')

class BaseDTO(ABC):
    @classmethod
    @abstractmethod
    def from_api_json(cls: Type[T], data: Dict[str, Any]) -> T:
        """Convert API JSON to DTO."""
        pass

    @abstractmethod
    def to_api_json(self) -> Dict[str, Any]:
        """Convert DTO to API JSON."""
        pass
    
    def validate(self) -> bool:
        """Validate the DTO. Returns True if valid, raises ValidationError otherwise."""
        return True

@dataclass
class BaseV8ResponseDTO:
    """Base class for all V8 API response wrappers."""
    createdTimestampUtcEpochSeconds: Optional[int] = None
    endpoint: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate the response DTO."""
        return True
