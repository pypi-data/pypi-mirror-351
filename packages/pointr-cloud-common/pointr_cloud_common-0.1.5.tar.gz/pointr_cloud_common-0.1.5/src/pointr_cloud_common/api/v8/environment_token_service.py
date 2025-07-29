import requests
import json
from typing import Dict, Any

class TokenError(Exception):
    """Exception raised for token-related errors."""
    pass

def get_access_token(client_id: str, api_url: str, username: str, password: str) -> Dict[str, Any]:
    """
    Get an access token from the V8 API.
    
    Args:
        client_id: Client identifier
        api_url: Base URL for the API
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        Dictionary containing the access token and other token information
    """
    url = f"{api_url}/api/v8/auth/token"
    
    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "username": username,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if not response.ok:
            error_msg = f"Failed to get access token: {response.status_code}"
            try:
                error_details = response.json()
                if isinstance(error_details, dict) and "error" in error_details:
                    error_msg += f", error: {error_details['error']}"
            except:
                error_msg += f", response: {response.text[:200]}"
            
            raise TokenError(error_msg)
        
        response_data = response.json()
        # V8 API wraps the token data in a "result" field
        if "result" in response_data:
            return response_data["result"]
        else:
            return response_data
    
    except requests.RequestException as e:
        raise TokenError(f"Request error: {str(e)}")

def refresh_access_token(client_id: str, api_url: str, refresh_token: str) -> Dict[str, Any]:
    """
    Refresh an access token using a refresh token.
    
    Args:
        client_id: Client identifier
        api_url: Base URL for the API
        refresh_token: Refresh token
        
    Returns:
        Dictionary containing the new access token and other token information
    """
    url = f"{api_url}/api/v8/auth/token"
    
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if not response.ok:
            error_msg = f"Failed to refresh access token: {response.status_code}"
            try:
                error_details = response.json()
                if isinstance(error_details, dict) and "error" in error_details:
                    error_msg += f", error: {error_details['error']}"
            except:
                error_msg += f", response: {response.text[:200]}"
            
            raise TokenError(error_msg)
        
        response_data = response.json()
        # V8 API wraps the token data in a "result" field
        if "result" in response_data:
            return response_data["result"]
        else:
            return response_data
    
    except requests.RequestException as e:
        raise TokenError(f"Request error: {str(e)}")
