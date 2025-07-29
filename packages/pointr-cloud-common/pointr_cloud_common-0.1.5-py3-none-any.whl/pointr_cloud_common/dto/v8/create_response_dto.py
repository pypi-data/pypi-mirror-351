from dataclasses import dataclass
from typing import Dict, Any, Optional

from pointr_cloud_common.dto.v8.base_dto import BaseDTO
from pointr_cloud_common.dto.v8.validation import ValidationError, validate_required_field, validate_type

@dataclass
class CreateResponseDTO(BaseDTO):
    fid: str

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "CreateResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for CreateResponseDTO")
        
        # Handle V8 API response format - extract from 'result' if present
        if "result" in data:
            result_data = data["result"]
        else:
            result_data = data
        
        # Map V8 API field names to our DTO field names
        fid = (result_data.get("fid") or 
               result_data.get("siteFid") or 
               result_data.get("buildingFid") or 
               result_data.get("levelFid") or 
               result_data.get("clientFid") or
               result_data.get("id"))
        
        if not fid:
            raise ValidationError("Missing required field 'fid' or equivalent", "fid", None)
        
        validate_type(fid, str, "fid")
        
        return CreateResponseDTO(fid=fid)

    def to_api_json(self) -> Dict[str, Any]:
        return {"fid": self.fid}
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.fid:
            raise ValidationError("fid cannot be empty", "fid", self.fid)
        return True
