from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v8.base_dto import BaseDTO, BaseV8ResponseDTO
from pointr_cloud_common.dto.v8.validation import ValidationError, validate_required_field, validate_type, ensure_dict

@dataclass
class BuildingDTO(BaseDTO):
    fid: str
    name: str
    sid: str  # Site ID
    extraData: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "BuildingDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for BuildingDTO")
        
        # Handle V8 API response format - extract from 'result' if present
        if "result" in data:
            data = data["result"]
        
        # Map V8 API field names to our DTO field names
        # V8 API likely uses buildingInternalIdentifier as the FID
        fid = (data.get("buildingInternalIdentifier") or 
               data.get("buildingFid") or 
               data.get("fid"))
        
        name = (data.get("buildingTitle") or 
                data.get("name"))
        
        # Site ID mapping
        sid = (data.get("siteInternalIdentifier") or 
               data.get("siteFid") or 
               data.get("sid"))
        
        extra_data = (data.get("buildingExtraData") or 
                     data.get("extraData") or 
                     data.get("extra", {}))
        
        if fid is None:
            raise ValidationError("Missing required field 'fid' (buildingInternalIdentifier/buildingFid/fid)", "fid", None)
        if not name:
            raise ValidationError("Missing required field 'name' (buildingTitle/name)", "name", None)
        if sid is None:
            raise ValidationError("Missing required field 'sid' (siteInternalIdentifier/siteFid/sid)", "sid", None)
        
        # Convert IDs to strings if they're numbers
        fid = str(fid)
        sid = str(sid)
        
        validate_type(fid, str, "fid")
        validate_type(name, str, "name")
        validate_type(sid, str, "sid")
        
        # Use the ensure_dict helper to safely handle extraData
        extra_data = ensure_dict(extra_data, "extraData")
        
        return BuildingDTO(
            fid=fid,
            name=name,
            sid=sid,
            extraData=extra_data
        )

    def to_api_json(self) -> Dict[str, Any]:
        return {
            "buildingInternalIdentifier": self.fid,
            "buildingTitle": self.name,
            "siteInternalIdentifier": self.sid,
            "buildingExtraData": self.extraData
        }
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.fid:
            raise ValidationError("fid cannot be empty", "fid", self.fid)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        if not self.sid:
            raise ValidationError("sid cannot be empty", "sid", self.sid)
        return True

    @staticmethod
    def list_from_api_json(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List["BuildingDTO"]:
        if isinstance(data, list):
            return [BuildingDTO.from_api_json(item) for item in data]
        
        # Handle V8 API response format
        if isinstance(data, dict):
            # Extract from 'results' field if present
            if "results" in data:
                results = data["results"]
                if isinstance(results, list):
                    return [BuildingDTO.from_api_json(item) for item in results]
            
            # Handle FeatureCollection format
            if data.get("type") == "FeatureCollection" and "features" in data:
                return [BuildingDTO.from_api_json(feature.get("properties", feature)) 
                       for feature in data["features"]]
            # Handle direct array format
            elif "items" in data and isinstance(data["items"], list):
                return [BuildingDTO.from_api_json(item) for item in data["items"]]
        
        return []

@dataclass
class BuildingResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for single building."""
    result: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "BuildingResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for BuildingResponseDTO")
        
        return BuildingResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            result=data.get("result")
        )

    def get_building(self) -> Optional[BuildingDTO]:
        """Extract building from the result."""
        if not self.result:
            return None
        return BuildingDTO.from_api_json(self.result)

@dataclass
class BuildingsResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for multiple buildings."""
    results: Optional[List[Dict[str, Any]]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "BuildingsResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for BuildingsResponseDTO")
        
        return BuildingsResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            results=data.get("results")
        )

    def get_buildings(self) -> List[BuildingDTO]:
        """Extract buildings from the results array."""
        if not self.results:
            return []
        return BuildingDTO.list_from_api_json(self.results)

@dataclass
class CreateBuildingResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for building creation."""
    result: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "CreateBuildingResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for CreateBuildingResponseDTO")
        
        return CreateBuildingResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            result=data.get("result")
        )

    def get_building(self) -> Optional[BuildingDTO]:
        """Extract created building from the result."""
        if not self.result:
            return None
        return BuildingDTO.from_api_json(self.result)
