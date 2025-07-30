from ..models.boundary import BoundarySearchRequest, LocationBoundarySearchRequest
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from typing import Dict, Optional

class BoundaryService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "boundarys/_search"
        
    def location_search_boundary(self, boundary_request: LocationBoundarySearchRequest,request_info: Optional[RequestInfo] = None) -> Dict:
        endpoint = f"/location/v11/{self.base_url}"
        request_info = request_info or RequestConfig.get_request_info()
        return self.api_client.post(
            endpoint,
            params=boundary_request.to_dict(),
            json_data=request_info
        )
        
    def boundary_search(self, boundary_request: BoundarySearchRequest) -> Dict:
        endpoint = f"{self.base_url}"
        return self.api_client.post(
            endpoint,
            params=boundary_request.to_dict()
        )
