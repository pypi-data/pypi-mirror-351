import logging
import requests
import json
import time
from typing import Dict, Any, Optional, List, Union, cast

from pointr_cloud_common.api.v8.base_service import V8ApiError
from pointr_cloud_common.api.v8.site_service import SiteApiService
from pointr_cloud_common.api.v8.building_service import BuildingApiService
from pointr_cloud_common.api.v8.level_service import LevelApiService
from pointr_cloud_common.api.v8.client_service import ClientApiService
from pointr_cloud_common.api.v8.sdk_service import SdkApiService
from pointr_cloud_common.api.v8.environment_token_service import get_access_token, refresh_access_token

class V8ApiService:
    def __init__(
        self,
        config: Dict[str, str],
        user_email: Optional[str] = None,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ):
        """
        Initialize the V8 API service with configuration and authentication.
        
        Args:
            config: Configuration for the API service containing:
                - api_url: Base URL for the API
                - client_identifier: Client identifier
                - username: Username for authentication (if token/refresh_token not provided)
                - password: Password for authentication (if token/refresh_token not provided)
            user_email: Optional user email for logging
            token: Optional pre-authenticated access token
            refresh_token: Optional refresh token to obtain a new access token if token not provided
        """
        self.base_url = config["api_url"]
        self.client_id = config["client_identifier"]
        self.user_email = user_email
        self.config = config
        self.logger = logging.getLogger(__name__)

        if token:
            self.token = token
        elif refresh_token:
            token_data = refresh_access_token(
                client_id=config["client_identifier"],
                api_url=config["api_url"],
                refresh_token=refresh_token
            )
            self.token = token_data["access_token"]
        else:
            token_data = get_access_token(
                client_id=config["client_identifier"],
                api_url=config["api_url"],
                username=config["username"],
                password=config["password"]
            )
            self.token = token_data["access_token"]

        # Initialize sub-services
        self.site_service = SiteApiService(self)
        self.building_service = BuildingApiService(self)
        self.level_service = LevelApiService(self)
        self.client_service = ClientApiService(self)
        self.sdk_service = SdkApiService(self)

    def _make_request(self, method: str, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the V8 API with error handling."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Track operation time
        start_time = time.time()
        operation_name = f"{method} {endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json_data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=json_data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Log the operation duration
            duration = time.time() - start_time
            self.logger.debug(f"API operation {operation_name} completed in {duration:.2f}s")
            
            if not response.ok:
                error_msg = f"API request failed: {response.status_code}"
                try:
                    error_details = response.json()
                    if isinstance(error_details, dict):
                        if "message" in error_details:
                            error_msg += f", message: {error_details['message']}"
                        elif "error" in error_details:
                            error_msg += f", error: {error_details['error']}"
                        else:
                            error_msg += f", details: {error_details}"
                    else:
                        error_msg += f", details: {error_details}"
                except:
                    error_msg += f", response: {response.text[:200]}"
                
                raise V8ApiError(
                    error_msg, 
                    status_code=response.status_code, 
                    response_text=response.text
                )
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # If the response is not JSON, return an empty dict
                if response.text.strip():
                    self.logger.warning(f"Non-JSON response from API: {response.text[:200]}")
                return {}
                
        except requests.RequestException as e:
            # Log the operation failure
            duration = time.time() - start_time
            self.logger.error(f"API operation {operation_name} failed after {duration:.2f}s: {str(e)}")
            raise V8ApiError(f"Request error: {str(e)}")

    # Site methods - delegated to site_service
    def get_sites(self) -> List[Any]:
        return self.site_service.get_sites()

    def get_draft_sites(self) -> List[Any]:
        return self.site_service.get_draft_sites()

    def get_site_by_fid(self, site_fid: str) -> Any:
        return self.site_service.get_site_by_fid(site_fid)

    def get_draft_site_by_fid(self, site_fid: str) -> Any:
        return self.site_service.get_draft_site_by_fid(site_fid)

    def create_site(self, site: Any) -> str:
        return self.site_service.create_site(site)

    def update_site(self, site_id: str, site: Any) -> str:
        return self.site_service.update_site(site_id, site)

    def delete_site(self, site_id: str) -> bool:
        return self.site_service.delete_site(site_id)

    def get_site_geometries(self) -> Dict[str, Any]:
        return self.site_service.get_site_geometries()

    def get_draft_site_geometries(self) -> Dict[str, Any]:
        return self.site_service.get_draft_site_geometries()

    # Building methods - delegated to building_service
    def get_buildings(self, site_fid: str) -> List[Any]:
        return self.building_service.get_buildings(site_fid)

    def get_draft_buildings(self, site_fid: str) -> List[Any]:
        return self.building_service.get_draft_buildings(site_fid)

    def get_building_by_fid(self, building_fid: str) -> Any:
        return self.building_service.get_building_by_fid(building_fid)

    def get_draft_building_by_fid(self, building_fid: str) -> Any:
        return self.building_service.get_draft_building_by_fid(building_fid)

    def create_building(self, site_fid: str, building: Any) -> str:
        return self.building_service.create_building(site_fid, building)

    def update_building(self, building_fid: str, building: Any) -> str:
        return self.building_service.update_building(building_fid, building)

    def delete_building(self, building_fid: str) -> bool:
        return self.building_service.delete_building(building_fid)

    # Level methods - delegated to level_service
    def get_levels(self, building_fid: str) -> List[Any]:
        return self.level_service.get_levels(building_fid)

    def get_draft_levels(self, building_fid: str) -> List[Any]:
        return self.level_service.get_draft_levels(building_fid)

    def get_level_by_index(self, building_fid: str, level_index: int) -> Any:
        return self.level_service.get_level_by_index(building_fid, level_index)

    def create_level(self, building_fid: str, level_index: int, level: Dict[str, Any]) -> str:
        return self.level_service.create_level(building_fid, level_index, level)

    def update_level(self, building_fid: str, level_index: int, level: Dict[str, Any]) -> str:
        return self.level_service.update_level(building_fid, level_index, level)

    def delete_level(self, building_fid: str, level_index: int) -> bool:
        return self.level_service.delete_level(building_fid, level_index)

    # Client methods - delegated to client_service
    def get_clients(self) -> List[Any]:
        return self.client_service.get_clients()

    def get_client_by_id(self, client_id: str) -> Any:
        return self.client_service.get_client_by_id(client_id)

    def update_client(self, client_id: str, client: Any) -> bool:
        return self.client_service.update_client(client_id, client)

    # SDK methods - delegated to sdk_service
    def get_default_keys(self) -> List[str]:
        return self.sdk_service.get_default_keys()

    def get_client_sdk_configurations(self, client_id: str) -> Dict[str, Any]:
        return self.sdk_service.get_client_sdk_configurations(client_id)

    def get_client_draft_sdk_configurations(self, client_id: str) -> Dict[str, Any]:
        return self.sdk_service.get_client_draft_sdk_configurations(client_id)

    def get_client_typed_sdk_configurations(self, client_id: str) -> List[Dict[str, Any]]:
        return self.sdk_service.get_client_typed_sdk_configurations(client_id)

    def get_site_typed_sdk_configurations(self, site_id: str) -> List[Dict[str, Any]]:
        return self.sdk_service.get_site_typed_sdk_configurations(site_id)

    def get_building_typed_sdk_configurations(self, building_id: str) -> List[Dict[str, Any]]:
        return self.sdk_service.get_building_typed_sdk_configurations(building_id)

    def update_client_sdk_configurations(self, client_id: str, configurations: List[Any]) -> bool:
        return self.sdk_service.update_client_sdk_configurations(client_id, configurations)

    def update_site_sdk_configurations(self, site_id: str, configurations: List[Any]) -> bool:
        return self.sdk_service.update_site_sdk_configurations(site_id, configurations)

    def update_building_sdk_configurations(self, building_id: str, configurations: List[Any]) -> bool:
        return self.sdk_service.update_building_sdk_configurations(building_id, configurations)
