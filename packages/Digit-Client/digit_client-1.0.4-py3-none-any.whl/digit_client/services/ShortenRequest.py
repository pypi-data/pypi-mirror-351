from ..models.ShortenRequest import ShortenRequest, ShortenRequestBuilder
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from typing import Dict, Optional
import requests

class ShortenRequestService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()

    def redirect_url(self, id: str) -> str:
        """
        Redirect to the original URL using the shortened ID
        
        Args:
            id (str): The shortened URL ID
            
        Returns:
            str: The original URL to redirect to
        """
        endpoint = f"/eus/{id}"
        
        return self.api_client.get(endpoint, require_auth=False)

    def shorten_url(self, 
                   shorten_request: ShortenRequest,
                   headers: Optional[Dict] = None) -> Dict:
        """ 
        Create a shortened URL
        
        Args:
            shorten_request (ShortenRequest): The request containing the URL to shorten
            headers (Optional[Dict]): Additional headers to include in the request
            
        Returns:
            Dict: Response containing the shortened URL information
        """
        payload = shorten_request.to_dict()
        
        endpoint = f"/eus/shortener"
        return self.api_client.post(
            endpoint,
            json_data=payload,
            additional_headers=headers,
            require_auth=False
        )


