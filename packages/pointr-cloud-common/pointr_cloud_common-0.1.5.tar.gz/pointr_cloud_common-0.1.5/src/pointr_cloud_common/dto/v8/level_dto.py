from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

from pointr_cloud_common.dto.v8.base_dto import BaseDTO, BaseV8ResponseDTO
from pointr_cloud_common.dto.v8.validation import ValidationError, validate_required_field, validate_type, ensure_dict

@dataclass
class LevelDTO(BaseDTO):
    fid: str
    name: str
    bid: str  # Building ID
    sid: str  # Site ID
    levelIndex: Optional[int] = None
    extraData: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "LevelDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for LevelDTO")
        
        # Handle V8 API response format - extract from 'result' if present
        if "result" in data:
            data = data["result"]
        
        # Map V8 API field names to our DTO field names
        # V8 API likely uses levelInternalIdentifier as the FID
        fid = (data.get("levelInternalIdentifier") or 
               data.get("levelFid") or 
               data.get("fid"))
        
        name = (data.get("levelTitle") or 
                data.get("name"))
        
        # Building ID mapping
        bid = (data.get("buildingInternalIdentifier") or 
               data.get("buildingFid") or 
               data.get("bid"))
        
        # Site ID mapping
        sid = (data.get("siteInternalIdentifier") or 
               data.get("siteFid") or 
               data.get("sid"))
        
        level_index = (data.get("levelIndex") or 
                      data.get("floorNumber"))
        
        extra_data = (data.get("levelExtraData") or 
                     data.get("extraData") or 
                     data.get("extra", {}))
        
        if fid is None:
            raise ValidationError("Missing required field 'fid' (levelInternalIdentifier/levelFid/fid)", "fid", None)
        if not name:
            raise ValidationError("Missing required field 'name' (levelTitle/name)", "name", None)
        if bid is None:
            raise ValidationError("Missing required field 'bid' (buildingInternalIdentifier/buildingFid/bid)", "bid", None)
        if sid is None:
            raise ValidationError("Missing required field 'sid' (siteInternalIdentifier/siteFid/sid)", "sid", None)
        
        # Convert IDs to strings if they're numbers
        fid = str(fid)
        bid = str(bid)
        sid = str(sid)
        
        validate_type(fid, str, "fid")
        validate_type(name, str, "name")
        validate_type(bid, str, "bid")
        validate_type(sid, str, "sid")
        
        # Extract optional levelIndex
        if level_index is not None:
            try:
                level_index = int(level_index)
            except (ValueError, TypeError):
                raise ValidationError("levelIndex must be convertible to int", "levelIndex", level_index)
        
        # Use the ensure_dict helper to safely handle extraData
        extra_data = ensure_dict(extra_data, "extraData")
        
        return LevelDTO(
            fid=fid,
            name=name,
            bid=bid,
            sid=sid,
            levelIndex=level_index,
            extraData=extra_data
        )

    def to_api_json(self) -> Dict[str, Any]:
        result = {
            "levelInternalIdentifier": self.fid,
            "levelTitle": self.name,
            "buildingInternalIdentifier": self.bid,
            "siteInternalIdentifier": self.sid,
            "levelExtraData": self.extraData
        }
        
        if self.levelIndex is not None:
            result["levelIndex"] = self.levelIndex
            
        return result
    
    @property
    def floorNumber(self) -> Optional[int]:
        """Alias for levelIndex for backward compatibility."""
        return self.levelIndex
    
    def validate(self) -> bool:
        """Validate the DTO."""
        if not self.fid:
            raise ValidationError("fid cannot be empty", "fid", self.fid)
        if not self.name:
            raise ValidationError("name cannot be empty", "name", self.name)
        if not self.bid:
            raise ValidationError("bid cannot be empty", "bid", self.bid)
        if not self.sid:
            raise ValidationError("sid cannot be empty", "sid", self.sid)
        return True

    @staticmethod
    def list_from_api_json(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List["LevelDTO"]:
        if isinstance(data, list):
            return [LevelDTO.from_api_json(item) for item in data]
        
        # Handle V8 API response format
        if isinstance(data, dict):
            # Extract from 'results' field if present
            if "results" in data:
                results = data["results"]
                if isinstance(results, list):
                    return [LevelDTO.from_api_json(item) for item in results]
            
            # Handle FeatureCollection format
            if data.get("type") == "FeatureCollection" and "features" in data:
                return [LevelDTO.from_api_json(feature.get("properties", feature)) 
                       for feature in data["features"]]
            # Handle direct array format
            elif "items" in data and isinstance(data["items"], list):
                return [LevelDTO.from_api_json(item) for item in data["items"]]
        
        return []

@dataclass
class BuildingLevelsResponseDTO(BaseV8ResponseDTO):
    """V8 API response wrapper for building levels."""
    results: Optional[List[Dict[str, Any]]] = None

    @staticmethod
    def from_api_json(data: Dict[str, Any]) -> "BuildingLevelsResponseDTO":
        if not isinstance(data, dict):
            raise ValidationError("Expected dictionary for BuildingLevelsResponseDTO")
        
        return BuildingLevelsResponseDTO(
            createdTimestampUtcEpochSeconds=data.get("createdTimestampUtcEpochSeconds"),
            endpoint=data.get("endpoint"),
            results=data.get("results")
        )

    def get_levels(self) -> List[LevelDTO]:
        """Extract levels from the results array."""
        if not self.results:
            return []
        return LevelDTO.list_from_api_json(self.results)
