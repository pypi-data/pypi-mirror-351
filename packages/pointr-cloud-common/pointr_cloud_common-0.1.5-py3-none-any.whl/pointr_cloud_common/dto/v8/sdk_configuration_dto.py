from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Set, ClassVar

from pointr_cloud_common.dto.v8.base_dto import BaseDTO, BaseV8ResponseDTO
from pointr_cloud_common.dto.v8.validation import ValidationError, validate_type

@dataclass
class SdkConfigurationDTO(BaseDTO):
    key: str
    value: str
    valueType: str
    
    # Class variables (not dataclass fields)
    VALID_VALUE_TYPES: ClassVar[Set[str]] = {"Float", "Double", "Integer", "Boolean", "String"}
    MAX_VALUE_LENGTH: ClassVar[int] = 5000

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "SdkConfigurationDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for SdkConfigurationDTO")
        
        # Handle V8 API response format - extract from 'result' if present
        if "result" in data:
            data = data["result"]
        
        # Map V8 API field names to our DTO field names
        key = (data.get("configurationKey") or 
               data.get("key") or 
               data.get("sdkConfigurationKey"))
        
        value = (data.get("configurationValue") or 
                data.get("value") or 
                data.get("sdkConfigurationValue"))
        
        value_type = (data.get("configurationValueType") or 
                     data.get("valueType") or 
                     data.get("ValueType") or 
                     data.get("sdkConfigurationValueType"))
        
        if not key:
            raise ValidationError("Missing key field (configurationKey/key/sdkConfigurationKey)", "key", None)
        if value is None:  # Allow empty string but not None
            raise ValidationError("Missing value field (configurationValue/value/sdkConfigurationValue)", "value", None)
        if not value_type:
            raise ValidationError("Missing valueType field (configurationValueType/valueType/sdkConfigurationValueType)", "valueType", None)
        
        validate_type(key, str, "key")
        validate_type(value, str, "value")
        validate_type(value_type, str, "valueType")
        
        return SdkConfigurationDTO(
            key=key,
            value=value,
            valueType=value_type
        )

    def to_api_json(self) -> Dict[str, Any]:
        """Convert the DTO to a dictionary for API requests."""
        return {
            "configurationKey": self.key,
            "configurationValue": self.value,
            "configurationValueType": self.valueType
        }
    
    def validate(self) -> bool:
        """Validate the DTO according to API requirements."""
        if not self.key:
            raise ValidationError("configurationKey cannot be empty", "key", self.key)
            
        if self.value is None:  # Allow empty string but not None
            raise ValidationError("configurationValue cannot be None", "value", self.value)
            
        if len(self.value) > self.MAX_VALUE_LENGTH:
            raise ValidationError(
                f"configurationValue exceeds maximum length of {self.MAX_VALUE_LENGTH} characters", 
                "value", 
                f"{len(self.value)} characters"
            )
            
        if not self.valueType:
            raise ValidationError("configurationValueType cannot be empty", "valueType", self.valueType)
            
        if self.valueType not in self.VALID_VALUE_TYPES:
            raise ValidationError(
                f"configurationValueType must be one of {', '.join(self.VALID_VALUE_TYPES)}", 
                "valueType", 
                self.valueType
            )
            
        return True

    @staticmethod
    def list_from_api_json(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List["SdkConfigurationDTO"]:
        if isinstance(data, list):
            return [SdkConfigurationDTO.from_api_json(item) for item in data]
        
        # Handle V8 API response format
        if isinstance(data, dict):
            # Extract from 'results' field if present
            if "results" in data:
                results = data["results"]
                if isinstance(results, list):
                    return [SdkConfigurationDTO.from_api_json(item) for item in results]
            
            # Handle nested configurations
            if "configurations" in data and isinstance(data["configurations"], list):
                return [SdkConfigurationDTO.from_api_json(item) for item in data["configurations"]]
        
        return []

@dataclass
class SdkConfigurationResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for SDK configurations."""
    result: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "SdkConfigurationResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for SdkConfigurationResponseDTO")
        
        return SdkConfigurationResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            result=data.get("result")
        )

    def get_sdk_configurations(self) -> List[SdkConfigurationDTO]:
        """Extract SDK configurations from the result."""
        if not self.result:
            return []
        
        # V8 API may return SDK configs in different formats
        if isinstance(self.result, list):
            return SdkConfigurationDTO.list_from_api_json(self.result)
        elif isinstance(self.result, dict):
            # Handle nested structure
            configs = self.result.get("configurations", [])
            if isinstance(configs, list):
                return SdkConfigurationDTO.list_from_api_json(configs)
        
        return []

@dataclass
class SdkTypedConfigResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for typed SDK configurations."""
    results: Optional[List[Dict[str, Any]]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "SdkTypedConfigResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for SdkTypedConfigResponseDTO")
        
        return SdkTypedConfigResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            results=data.get("results")
        )

    def get_sdk_configurations(self) -> List[SdkConfigurationDTO]:
        """Extract SDK configurations from the results array."""
        if not self.results:
            return []
        return SdkConfigurationDTO.list_from_api_json(self.results)
