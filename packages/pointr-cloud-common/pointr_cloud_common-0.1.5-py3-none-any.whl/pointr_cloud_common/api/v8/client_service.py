from typing import Dict, Any, List, Optional
import logging
from pointr_cloud_common.dto.v8.client_dto import ClientDTO
from pointr_cloud_common.api.v8.base_service import BaseApiService, V8ApiError

class ClientApiService(BaseApiService):
    """Service for client-related API operations."""
    
    def __init__(self, api_service):
        super().__init__(api_service)
        self.logger = logging.getLogger(__name__)
    
    def get_clients(self) -> List[ClientDTO]:
        """
        Get all clients.
        
        Returns:
            A list of ClientDTO objects
        """
        endpoint = "api/v8/clients"
        data = self._make_request("GET", endpoint)
        try:
            # V8 API returns clients in 'results' array
            self.logger.info(f"Retrieved clients data, found {len(data.get('results', []))} clients")
            return ClientDTO.list_from_api_json(data)
        except Exception as e:
            self.logger.error(f"Failed to parse clients: {str(e)}")
            raise V8ApiError(f"Failed to parse clients: {str(e)}")
    
    def get_client_by_id(self, client_id: str) -> ClientDTO:
        """
        Get a client by its ID.
        
        Args:
            client_id: The client ID
            
        Returns:
            A ClientDTO object
        """
        endpoint = f"api/v8/clients/{client_id}"
        data = self._make_request("GET", endpoint)
        
        # Simple logging without the full response
        self.logger.info(f"Retrieved client data for {client_id}")
        
        try:
            # V8 API returns single client in 'result' object
            if "result" in data:
                return ClientDTO.from_api_json(data["result"])
            else:
                return ClientDTO.from_api_json(data)
        except Exception as e:
            self.logger.error(f"Error parsing client {client_id}: {str(e)}")
            raise V8ApiError(f"Failed to parse client: {str(e)}")
    
    def update_client(self, client_id: str, client: ClientDTO) -> bool:
        """
        Update a client.
        
        Args:
            client_id: The client ID
            client: The client DTO with updated data
            
        Returns:
            True if the client was updated successfully
        """
        endpoint = f"api/v8/clients/{client_id}"
        
        # Create a payload from the client DTO
        payload = client.to_api_json()
        
        self.logger.info(f"Updating client with ID: {client_id}")
        self._make_request("PATCH", endpoint, payload)
        return True
