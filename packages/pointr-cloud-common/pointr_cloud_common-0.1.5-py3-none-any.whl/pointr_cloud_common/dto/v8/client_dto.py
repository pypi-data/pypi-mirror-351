from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v8.base_dto import BaseDTO, BaseV8ResponseDTO
from pointr_cloud_common.dto.v8.validation import ValidationError, validate_required_field, validate_type, ensure_dict

@dataclass
class ClientDTO(BaseDTO):
    identifier: str
    name: str
    extraData: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "ClientDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for ClientDTO")
        
        # Handle V8 API response format - extract from 'result' if present
        if "result" in data:
            data = data["result"]
        
        # Map V8 API field names to our DTO field names
        identifier = data.get("clientInternalIdentifier") or data.get("identifier")
        name = data.get("clientTitle") or data.get("name")
        extra_data = data.get("clientExtraData") or data.get("extraData", {})
        
        if not identifier:
            raise ValidationError("Missing required field 'identifier' or 'clientInternalIdentifier'", "identifier", None)
        if not name:
            raise ValidationError("Missing required field 'name' or 'clientTitle'", "name", None)
        
        return ClientDTO(
            identifier=str(identifier),
            name=str(name),
            extraData=ensure_dict(extra_data, "extraData")
        )

    @staticmethod
    def list_from_api_json(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List["ClientDTO"]:
        """
        Parse a list of clients from V8 API JSON response.
        
        Args:
            data: The API response data (can be a dict with 'results' or a list)
        
        Returns:
            A list of ClientDTO objects
        """
        if isinstance(data, list):
            return [ClientDTO.from_api_json(item) for item in data]
        
        # Handle V8 API response format
        if isinstance(data, dict):
            # Extract from 'results' field if present
            if "results" in data:
                results = data["results"]
                if isinstance(results, list):
                    return [ClientDTO.from_api_json(item) for item in results]
        
        return []

    def to_api_json(self) -> Dict[str, Any]:
        return {
            "clientInternalIdentifier": self.identifier,
            "clientTitle": self.name,
            "clientExtraData": self.extraData
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.identifier:
            raise ValidationError("identifier cannot be empty", "identifier", self.identifier)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        return True

@dataclass
class ClientResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for single client."""
    result: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "ClientResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for ClientResponseDTO")
        
        return ClientResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            result=data.get("result")
        )

    def get_client(self) -> Optional[ClientDTO]:
        """Extract client from the result."""
        if not self.result:
            return None
        return ClientDTO.from_api_json(self.result)

@dataclass
class ClientsResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for multiple clients."""
    results: Optional[List[Dict[str, Any]]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "ClientsResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for ClientsResponseDTO")
        
        return ClientsResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            results=data.get("results")
        )

    def get_clients(self) -> List[ClientDTO]:
        """Extract clients from the results array."""
        if not self.results:
            return []
        return [ClientDTO.from_api_json(item) for item in self.results]
