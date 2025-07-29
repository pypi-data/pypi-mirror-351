from typing import Dict, Any, List, Optional
import logging
from pointr_cloud_common.dto.v8.site_dto import SiteDTO
from pointr_cloud_common.dto.v8.create_response_dto import CreateResponseDTO
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError

class SiteApiService(BaseApiService):
    """Service for site-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_sites(self) -> List[SiteDTO]:
        """
        Get all sites for the client.
        
        Returns:
            A list of SiteDTO objects
        """
        endpoint = "api/v8/sites"
        data = self._make_request("GET", endpoint)
        try:
            # V8 API returns sites in 'results' array
            self.logger.info(f"Retrieved sites data, found {len(data.get('results', []))} sites")
            return SiteDTO.list_from_api_json(data)
        except Exception as e:
            self.logger.error(f"Failed to parse sites: {str(e)}")
            raise V8ApiError(f"Failed to parse sites: {str(e)}")

    def get_draft_sites(self) -> List[SiteDTO]:
        """
        Get all draft sites for the client.
        
        Returns:
            A list of SiteDTO objects
        """
        endpoint = "api/v8/sites/draft"
        data = self._make_request("GET", endpoint)
        try:
            # V8 API returns sites in 'results' array
            self.logger.info(f"Retrieved draft sites data, found {len(data.get('results', []))} draft sites")
            return SiteDTO.list_from_api_json(data)
        except Exception as e:
            self.logger.error(f"Failed to parse draft sites: {str(e)}")
            raise V8ApiError(f"Failed to parse draft sites: {str(e)}")

    def create_site(self, site: SiteDTO) -> str:
        """
        Create a site in the target environment.
        
        Args:
            site: The site DTO to create
            
        Returns:
            The FID of the created site
        """
        endpoint = "api/v8/sites"
        
        # Create a payload from the site DTO
        payload = site.to_api_json()
        
        self.logger.info(f"Creating site with name: {site.name}")
        data = self._make_request("POST", endpoint, payload)
        try:
            # V8 API returns created site in 'result' object
            if "result" in data:
                return CreateResponseDTO.from_api_json(data).fid
            else:
                return CreateResponseDTO.from_api_json(data).fid
        except Exception as e:
            self.logger.error(f"Failed to parse create response: {str(e)}")
            raise V8ApiError(f"Failed to parse create response: {str(e)}")

    def update_site(self, site_id: str, site: SiteDTO) -> str:
        """
        Update a site in the target environment.
        
        Args:
            site_id: The ID of the site to update
            site: The site DTO with updated data
            
        Returns:
            The FID of the updated site
        """
        endpoint = f"api/v8/sites/{site_id}"
        
        # Create a payload from the site DTO
        payload = site.to_api_json()
        
        self.logger.info(f"Updating site with ID: {site_id}")
        self._make_request("PATCH", endpoint, payload)
        return site_id

    def delete_site(self, site_id: str) -> bool:
        """
        Delete a site.
        
        Args:
            site_id: The ID of the site to delete
            
        Returns:
            True if the site was deleted successfully
        """
        endpoint = f"api/v8/sites/{site_id}"
        self._make_request("DELETE", endpoint)
        return True

    def get_site_by_fid(self, site_fid: str) -> SiteDTO:
        """
        Get a site by its FID.
        
        Args:
            site_fid: The site FID
            
        Returns:
            A SiteDTO object
        """
        endpoint = f"api/v8/sites/{site_fid}"
        data = self._make_request("GET", endpoint)
        
        # Simple logging without the full response
        self.logger.info(f"Retrieved site data for {site_fid}")
        
        try:
            # V8 API returns single site in 'result' object
            if "result" in data:
                return SiteDTO.from_api_json(data["result"])
            else:
                return SiteDTO.from_api_json(data)
        except Exception as e:
            self.logger.error(f"Error parsing site {site_fid}: {str(e)}")
            raise V8ApiError(f"Failed to parse site: {str(e)}")

    def get_draft_site_by_fid(self, site_fid: str) -> SiteDTO:
        """
        Get a draft site by its FID.
        
        Args:
            site_fid: The site FID
            
        Returns:
            A SiteDTO object
        """
        endpoint = f"api/v8/sites/{site_fid}/draft"
        data = self._make_request("GET", endpoint)
        
        # Simple logging without the full response
        self.logger.info(f"Retrieved draft site data for {site_fid}")
        
        try:
            # V8 API returns single site in 'result' object
            if "result" in data:
                return SiteDTO.from_api_json(data["result"])
            else:
                return SiteDTO.from_api_json(data)
        except Exception as e:
            self.logger.error(f"Error parsing draft site {site_fid}: {str(e)}")
            raise V8ApiError(f"Failed to parse draft site: {str(e)}")

    def get_site_geometries(self) -> Dict[str, Any]:
        """
        Get site geometries for the client.
        
        Returns:
            Site geometries data
        """
        endpoint = "api/v8/sites/geometries"
        return self._make_request("GET", endpoint)

    def get_draft_site_geometries(self) -> Dict[str, Any]:
        """
        Get draft site geometries for the client.
        
        Returns:
            Draft site geometries data
        """
        endpoint = "api/v8/sites/geometries/draft"
        return self._make_request("GET", endpoint)
