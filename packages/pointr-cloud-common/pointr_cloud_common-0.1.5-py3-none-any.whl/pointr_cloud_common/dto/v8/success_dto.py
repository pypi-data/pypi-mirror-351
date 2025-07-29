from dataclasses import dataclass
from typing import Dict, Any, Optional

from pointr_cloud_common.dto.v8.base_dto import BaseDTO, BaseV8ResponseDTO
from pointr_cloud_common.dto.v8.validation import ValidationError

@dataclass
class SuccessResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for success responses."""
    result: Optional[Dict[str, Any]] = None
    success: Optional[bool] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "SuccessResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for SuccessResponseDTO")
        
        # Extract success from various possible fields
        success = (data.get("success") or 
                  data.get("isSuccess") or 
                  data.get("successful"))
        
        return SuccessResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            result=data.get("result"),
            success=success
        )

    def is_successful(self) -> bool:
        """Check if the operation was successful."""
        if self.success is not None:
            return self.success
        
        # If no explicit success field, assume success if we have a result
        return self.result is not None

@dataclass
class EmptyResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for empty responses (like DELETE operations)."""
    
    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "EmptyResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for EmptyResponseDTO")
        
        return EmptyResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint")
        )
