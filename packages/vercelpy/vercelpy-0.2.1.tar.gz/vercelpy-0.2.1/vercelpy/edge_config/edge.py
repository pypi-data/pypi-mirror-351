import os
import requests
from typing import Dict, List, Optional, Any
import copy

from .errors import UnexpectedNetworkError, EdgeConfigError
from .connection import Connection, parse_connection_string

# Default client instance
_default_client = None

class EdgeConfigClient:
    def __init__(self, connection: Connection, options: Dict[str, Any] = None):
        self.connection = connection
        self.options = options or {}
        self.edge_config_id = connection["id"]
        self.base_url = connection["baseUrl"]
        self.version = connection["version"]
        
        # Set up headers
        self.headers = {
            "Authorization": f"Bearer {connection['token']}"
        }
    
    def _get_headers_for_request(self, options: Dict[str, Any] = None) -> Dict[str, str]:
        """Prepare headers for a request, handling options like consistentRead."""
        headers = self.headers.copy()
        if options and options.get("consistentRead"):
            headers["x-edge-config-min-updated-at"] = str(2**53 - 1)
        return headers
        
    def get(self, key: str, options: Dict[str, Any] = None) -> Any:
        """Get a value by key."""
        if not isinstance(key, str):
            raise ValueError("Expected key to be a string")
        
        if key.strip() == "":
            return None
        
        headers = self._get_headers_for_request(options)
        url = f"{self.base_url}/item/{key}?version={self.version}"
        res = requests.get(url, headers=headers)
        
        if res.ok:
            return res.json()
        
        # Handle errors
        if res.status_code == 401:
            raise Exception(EdgeConfigError.UNAUTHORIZED)
        if res.status_code == 404:
            if "x-edge-config-digest" in res.headers:
                return None
            raise Exception(EdgeConfigError.EDGE_CONFIG_NOT_FOUND)
        
        raise UnexpectedNetworkError(res)
    
    def has(self, key: str, options: Dict[str, Any] = None) -> bool:
        """Check if a key exists."""
        if not isinstance(key, str):
            raise ValueError("Expected key to be a string")
        
        if key.strip() == "":
            return False
        
        headers = self._get_headers_for_request(options)
        url = f"{self.base_url}/item/{key}?version={self.version}"
        res = requests.head(url, headers=headers)
        
        if res.status_code == 401:
            raise Exception(EdgeConfigError.UNAUTHORIZED)
        if res.status_code == 404:
            if "x-edge-config-digest" in res.headers:
                return False
            raise Exception(EdgeConfigError.EDGE_CONFIG_NOT_FOUND)
        
        return res.ok
    
    def get_all(self, keys: List[str] = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get all values or specified keys."""
        if keys is not None:
            if not isinstance(keys, list):
                raise ValueError("Expected keys to be an array of strings")
            
            for key in keys:
                if not isinstance(key, str):
                    raise ValueError("Expected keys to be an array of strings")
        
        headers = self._get_headers_for_request(options)
        
        # Build URL with query parameters for keys if provided
        url = f"{self.base_url}/items?version={self.version}"
        if keys:
            filtered_keys = [k for k in keys if isinstance(k, str) and k.strip() != ""]
            if not filtered_keys:
                return {}
            
            params = "&".join([f"key={k}" for k in filtered_keys])
            url = f"{url}&{params}"
        
        res = requests.get(url, headers=headers)
        
        if res.ok:
            return res.json()
        
        # Handle errors
        if res.status_code == 401:
            raise Exception(EdgeConfigError.UNAUTHORIZED)
        if res.status_code == 404:
            raise Exception(EdgeConfigError.EDGE_CONFIG_NOT_FOUND)
        
        raise UnexpectedNetworkError(res)
    
    def digest(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get the configuration digest."""
        headers = self._get_headers_for_request(options)
        url = f"{self.base_url}/digest?version={self.version}"
        res = requests.get(url, headers=headers)
        
        if res.ok:
            return res.json()
        
        raise UnexpectedNetworkError(res)


def create_client_from_env(options: Dict[str, Any] = None) -> Optional[EdgeConfigClient]:
    """Create a client using the EDGE_CONFIG environment variable."""
    connection_string = os.environ.get('EDGE_CONFIG')
    print("connection_string from env: " + connection_string)
    if not connection_string:
        return None
    
    connection = parse_connection_string(connection_string)
    if not connection:
        raise ValueError("Invalid connection string in EDGE_CONFIG environment variable")
    
    return EdgeConfigClient(connection, options)


def create_client(connection_string: str, options: Dict[str, Any] = None) -> EdgeConfigClient:
    """Create a new Edge Config client.
    
    The connection_string is required when calling this function directly.
    """
    if not connection_string:
        raise ValueError("Connection string is required")
    
    connection = parse_connection_string(connection_string)
    if not connection:
        raise ValueError("Invalid connection string provided")
    
    return EdgeConfigClient(connection, options)


def _init():
    """Initialize the default client if not already done."""
    global _default_client
    if not _default_client:
        _default_client = create_client_from_env()


def get(key: str, options: Dict[str, Any] = None) -> Any:
    """Get a value by key using the default client."""
    _init()
    if not _default_client:
        raise ValueError("EDGE_CONFIG environment variable not set")
    return _default_client.get(key, options)


def has(key: str, options: Dict[str, Any] = None) -> bool:
    """Check if a key exists using the default client."""
    _init()
    if not _default_client:
        raise ValueError("EDGE_CONFIG environment variable not set")
    return _default_client.has(key, options)


def get_all(keys: List[str] = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get all values or specified keys using the default client."""
    _init()
    if not _default_client:
        raise ValueError("EDGE_CONFIG environment variable not set")
    return _default_client.get_all(keys, options)


def digest(options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get the configuration digest using the default client."""
    _init()
    if not _default_client:
        raise ValueError("EDGE_CONFIG environment variable not set")
    return _default_client.digest(options)


def clone(value):
    """Deep clone a value."""
    return copy.deepcopy(value)