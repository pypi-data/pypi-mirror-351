"""TinyToken Python SDK"""

import requests

__version__ = "0.1.0"
__all__ = ["compress", "TinyTokenError"]


class TinyTokenError(Exception):
    """Exception raised for TinyToken API errors."""
    pass

class TinyToken:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def compress(self, text: str, quality: float) -> str:
        return compress(text, quality, self.api_key)

def compress(text: str, quality: float, api_key: str) -> str:
    """
    Compress text using the TinyToken API.
    
    Args:
        text: Text to compress (required)
        api_key: API key for authentication (required)
    
    Returns:
        Compressed text as string
    
    Raises:
        TinyTokenError: For any API errors
    """
    
    if not isinstance(api_key, str) or not api_key.strip():
        raise TinyTokenError("API key must be a non-empty string")
    
    try:
        response = requests.post(
            "https://api.tinytoken.org/compress",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "quality": quality
            },
            timeout=30
        )
        
        if response.status_code == 401:
            raise TinyTokenError("Invalid API key")
        elif response.status_code == 400:
            raise TinyTokenError("Invalid request parameters")
        elif response.status_code == 429:
            raise TinyTokenError("Rate limit exceeded")
        elif not response.ok:
            raise TinyTokenError(f"API error: {response.status_code}")
        
        data = response.json()
        
        if "compressed_text" not in data:
            raise TinyTokenError("Invalid response format")
        
        return data["compressed_text"]
        
    except requests.exceptions.Timeout:
        raise TinyTokenError("Request timeout")
    except requests.exceptions.ConnectionError:
        raise TinyTokenError("Connection error")
    except requests.exceptions.RequestException as e:
        raise TinyTokenError(f"Request failed: {str(e)}")
    except ValueError as e:
        raise TinyTokenError(f"Invalid JSON response: {str(e)}")