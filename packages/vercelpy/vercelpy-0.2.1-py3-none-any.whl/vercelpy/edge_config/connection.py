from typing import Dict, Optional, TypedDict
from urllib.parse import urlparse, parse_qs

_VERCEL_EDGE_CONFIG_API_URL = "https://edge-config.vercel.com/"

class Connection(TypedDict):
    type: str
    baseUrl: str
    id: str
    version: str
    token: str


def parse_connection_string(connection_string: str) -> Optional[Connection]:
    """Parse a connection string into a Connection object."""
    if not connection_string:
        return None
    
    # Try parsing as query params
    if connection_string.startswith("edge-config:"):
        params = dict(item.split("=", 1) for item in connection_string[12:].split("&") if "=" in item)
        if "id" in params and "token" in params:
            return {
                "type": "vercel",
                "baseUrl": f"{_VERCEL_EDGE_CONFIG_API_URL}{params['id']}",
                "id": params["id"],
                "version": "1",
                "token": params["token"]
            }
    
    # Try parsing as URL
    try:
        url = urlparse(connection_string)
        
        # Vercel connection
        if url.hostname == "edge-config.vercel.com":
            if url.scheme != "https":
                raise ValueError("Invalid connection string provided. Expected to start with 'https://'")
            
            path_parts = url.path.strip("/").split("/")
            id = path_parts[0] if path_parts else None
            
            if not id:
                raise ValueError("Invalid connection string provided. Expected to have an ID")
            
            query = parse_qs(url.query)
            token = query.get("token", [""])[0]
            if not token:
                raise ValueError("Invalid connection string provided. Expected to have a token")
            
            return {
                "type": "vercel",
                "baseUrl": f"{_VERCEL_EDGE_CONFIG_API_URL}{id}",
                "id": id,
                "version": "1",
                "token": token
            }
        
        # External connection
        else:
            query = parse_qs(url.query)
            id = query.get("id", [None])[0]
            token = query.get("token", [None])[0]
            version = query.get("version", ["1"])[0]
            
            if not id and url.path.startswith("/ecfg_"):
                id = url.path.split("/")[1]
            
            if not id or not token:
                return None
                
            base_url = f"{url.scheme}://{url.netloc}{url.path}"
            return {
                "type": "external",
                "baseUrl": base_url,
                "id": id,
                "token": token,
                "version": version
            }
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        return None
    
    return None 