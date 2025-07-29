from typing import Dict, Any, List, Optional
import logging
from pointr_cloud_common.dto.v8.building_dto import BuildingDTO
from pointr_cloud_common.dto.v8.create_response_dto import CreateResponseDTO
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError

class BuildingApiService(BaseApiService):
    """Service for building-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_buildings(self, site_fid: str) -> List[BuildingDTO]:
        """
        Get all buildings for a site.
        
        Args:
            site_fid: The site FID
        
        Returns:
            A list of BuildingDTO objects
        """
        endpoint = f"api/v8/sites/{site_fid}/buildings"
        data = self._make_request("GET", endpoint)
        try:
            # V8 API returns buildings in 'results' array
            self.logger.info(f"Retrieved buildings data for site {site_fid}, found {len(data.get('results', []))} buildings")
            return BuildingDTO.list_from_api_json(data)
        except Exception as e:
            self.logger.error(f"Failed to parse buildings: {str(e)}")
            raise V8ApiError(f"Failed to parse buildings: {str(e)}")
    
    def get_draft_buildings(self, site_fid: str) -> List[BuildingDTO]:
        """
        Get all draft buildings for a site.
        
        Args:
            site_fid: The site FID
        
        Returns:
            A list of BuildingDTO objects
        """
        endpoint = f"api/v8/sites/{site_fid}/buildings/draft"
        data = self._make_request("GET", endpoint)
        try:
            # V8 API returns buildings in 'results' array
            self.logger.info(f"Retrieved draft buildings data for site {site_fid}, found {len(data.get('results', []))} draft buildings")
            return BuildingDTO.list_from_api_json(data)
        except Exception as e:
            self.logger.error(f"Failed to parse draft buildings: {str(e)}")
            raise V8ApiError(f"Failed to parse draft buildings: {str(e)}")
    
    def get_building_by_fid(self, building_fid: str) -> BuildingDTO:
        """
        Get a building by its FID.
        
        Args:
            building_fid: The building FID
        
        Returns:
            A BuildingDTO object
        """
        endpoint = f"api/v8/buildings/{building_fid}"
        data = self._make_request("GET", endpoint)
        
        # Simple logging without the full response
        self.logger.info(f"Retrieved building data for {building_fid}")
        
        try:
            # V8 API returns single building in 'result' object
            if "result" in data:
                return BuildingDTO.from_api_json(data["result"])
            else:
                return BuildingDTO.from_api_json(data)
        except Exception as e:
            self.logger.error(f"Error parsing building {building_fid}: {str(e)}")
            raise V8ApiError(f"Failed to parse building: {str(e)}")
    
    def get_draft_building_by_fid(self, building_fid: str) -> BuildingDTO:
        """
        Get a draft building by its FID.
        
        Args:
            building_fid: The building FID
        
        Returns:
            A BuildingDTO object
        """
        endpoint = f"api/v8/buildings/{building_fid}/draft"
        data = self._make_request("GET", endpoint)
        
        # Simple logging without the full response
        self.logger.info(f"Retrieved draft building data for {building_fid}")
        
        try:
            # V8 API returns single building in 'result' object
            if "result" in data:
                return BuildingDTO.from_api_json(data["result"])
            else:
                return BuildingDTO.from_api_json(data)
        except Exception as e:
            self.logger.error(f"Error parsing draft building {building_fid}: {str(e)}")
            raise V8ApiError(f"Failed to parse draft building: {str(e)}")
    
    def create_building(self, site_fid: str, building: BuildingDTO) -> str:
        """
        Create a building in the target environment.
        
        Args:
            site_fid: The site FID
            building: The building DTO to create
            
        Returns:
            The FID of the created building
        """
        endpoint = f"api/v8/sites/{site_fid}/buildings"
        
        # Create a payload from the building DTO
        payload = building.to_api_json()
        
        self.logger.info(f"Creating building with name: {building.name}")
        data = self._make_request("POST", endpoint, payload)
        try:
            # V8 API returns created building in 'result' object
            if "result" in data:
                return CreateResponseDTO.from_api_json(data).fid
            else:
                return CreateResponseDTO.from_api_json(data).fid
        except Exception as e:
            self.logger.error(f"Failed to parse create response: {str(e)}")
            raise V8ApiError(f"Failed to parse create response: {str(e)}")
    
    def update_building(self, building_fid: str, building: BuildingDTO) -> str:
        """
        Update a building in the target environment.
        
        Args:
            building_fid: The building FID
            building: The building DTO with updated data
            
        Returns:
            The FID of the updated building
        """
        endpoint = f"api/v8/buildings/{building_fid}"
        
        # Create a payload from the building DTO
        payload = building.to_api_json()
        
        self.logger.info(f"Updating building with ID: {building_fid}")
        self._make_request("PATCH", endpoint, payload)
        return building_fid
    
    def delete_building(self, building_fid: str) -> bool:
        """
        Delete a building.
        
        Args:
            building_fid: The building FID
            
        Returns:
            True if the building was deleted successfully
        """
        endpoint = f"api/v8/buildings/{building_fid}"
        self._make_request("DELETE", endpoint)
        return True
