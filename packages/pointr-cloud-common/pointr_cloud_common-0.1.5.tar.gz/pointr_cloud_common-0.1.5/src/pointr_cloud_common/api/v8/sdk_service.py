from typing import Dict, Any, List, Optional
import logging
from pointr_cloud_common.dto.v8.sdk_configuration_dto import SdkConfigurationDTO
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError

class SdkApiService(BaseApiService):
    """Service for SDK configuration-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_default_keys(self) -> List[str]:
        """
        Get default keys of SDK configurations.
        
        Returns:
            A list of default keys
        """
        endpoint = "api/v8/configurations/sdk-configurations/default-keys"
        data = self._make_request("GET", endpoint)
        try:
            self.logger.info(f"Retrieved default keys, found {len(data.get('results', []))} keys")
            return data.get("results", [])
        except Exception as e:
            self.logger.error(f"Failed to parse default keys: {str(e)}")
            raise V8ApiError(f"Failed to parse default keys: {str(e)}")
    
    def get_client_sdk_configurations(self, client_id: str) -> Dict[str, Any]:
        """
        Get SDK configurations for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            SDK configurations data
        """
        endpoint = f"api/v8/clients/{client_id}/configurations/sdk-configurations"
        return self._make_request("GET", endpoint)
    
    def get_client_draft_sdk_configurations(self, client_id: str) -> Dict[str, Any]:
        """
        Get draft SDK configurations for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            Draft SDK configurations data
        """
        endpoint = f"api/v8/clients/{client_id}/configurations/sdk-configurations/draft"
        return self._make_request("GET", endpoint)
    
    def get_client_typed_sdk_configurations(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get typed SDK configurations for a client.
        
        Args:
            client_id: The client ID
            
        Returns:
            A list of typed SDK configurations
        """
        endpoint = f"api/v8/clients/{client_id}/configurations/sdk-configurations/typed"
        data = self._make_request("GET", endpoint)
        self.logger.info(f"Retrieved typed SDK configurations for client {client_id}, found {len(data.get('results', []))} configurations")
        return data.get("results", [])
    
    def get_site_typed_sdk_configurations(self, site_id: str) -> List[Dict[str, Any]]:
        """
        Get typed SDK configurations for a site.
        
        Args:
            site_id: The site ID
            
        Returns:
            A list of typed SDK configurations
        """
        endpoint = f"api/v8/sites/{site_id}/configurations/sdk-configurations/typed"
        data = self._make_request("GET", endpoint)
        self.logger.info(f"Retrieved typed SDK configurations for site {site_id}, found {len(data.get('results', []))} configurations")
        return data.get("results", [])
    
    def get_building_typed_sdk_configurations(self, building_id: str) -> List[Dict[str, Any]]:
        """
        Get typed SDK configurations for a building.
        
        Args:
            building_id: The building ID
            
        Returns:
            A list of typed SDK configurations
        """
        endpoint = f"api/v8/buildings/{building_id}/configurations/sdk-configurations/typed"
        data = self._make_request("GET", endpoint)
        self.logger.info(f"Retrieved typed SDK configurations for building {building_id}, found {len(data.get('results', []))} configurations")
        return data.get("results", [])
    
    def update_client_sdk_configurations(self, client_id: str, configurations: List[SdkConfigurationDTO]) -> bool:
        """
        Update SDK configurations for a client.
        
        Args:
            client_id: The client ID
            configurations: A list of SDK configuration DTOs
            
        Returns:
            True if the configurations were updated successfully
        """
        endpoint = f"api/v8/clients/{client_id}/configurations/sdk-configurations"
        
        # Create a payload from the configuration DTOs
        payload = [config.to_api_json() for config in configurations]
        
        self.logger.info(f"Updating SDK configurations for client: {client_id}")
        self._make_request("POST", endpoint, payload)
        return True
    
    def update_site_sdk_configurations(self, site_id: str, configurations: List[SdkConfigurationDTO]) -> bool:
        """
        Update SDK configurations for a site.
        
        Args:
            site_id: The site ID
            configurations: A list of SDK configuration DTOs
            
        Returns:
            True if the configurations were updated successfully
        """
        endpoint = f"api/v8/sites/{site_id}/configurations/sdk-configurations"
        
        # Create a payload from the configuration DTOs
        payload = [config.to_api_json() for config in configurations]
        
        self.logger.info(f"Updating SDK configurations for site: {site_id}")
        self._make_request("POST", endpoint, payload)
        return True
    
    def update_building_sdk_configurations(self, building_id: str, configurations: List[SdkConfigurationDTO]) -> bool:
        """
        Update SDK configurations for a building.
        
        Args:
            building_id: The building ID
            configurations: A list of SDK configuration DTOs
            
        Returns:
            True if the configurations were updated successfully
        """
        endpoint = f"api/v8/buildings/{building_id}/configurations/sdk-configurations"
        
        # Create a payload from the configuration DTOs
        payload = [config.to_api_json() for config in configurations]
        
        self.logger.info(f"Updating SDK configurations for building: {building_id}")
        self._make_request("POST", endpoint, payload)
        return True
