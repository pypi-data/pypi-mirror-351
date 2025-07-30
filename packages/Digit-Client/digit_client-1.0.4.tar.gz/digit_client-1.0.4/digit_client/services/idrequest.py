from typing import Dict, List, Optional, Any
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.idrequest import IdRequest, IdRequestBuilder

class IdRequestService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "/egov-idgen/id"
        
    def generate_id(self, id_request: List[IdRequest],request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Generate IDs based on the provided request parameters
        
        Args:
            id_request: IdRequest object containing request parameters
            request_info: RequestInfo object containing request information

        Returns:
            Dict: Response containing generated IDs
        """
        request_info = request_info or RequestConfig.get_request_info()

        print(IdRequest)
        # Create IdRequest structure
        payload = {
            'RequestInfo': request_info.to_dict(),
            'idRequest': [req.to_dict() for req in id_request]
        }
        endpoint = f"{self.base_url}/_generate"
        return self.api_client.post(
            endpoint,
            json_data=payload
        )
        
            
        
