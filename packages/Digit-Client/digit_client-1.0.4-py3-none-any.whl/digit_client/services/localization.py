from typing import List, Dict, Optional
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.localization import (
    Message, CreateMessagesRequest,
    UpdateMessageRequest, DeleteMessagesRequest,
    LocaleRequest
)

class LocalizationService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "localization/messages/v1"

    def create_messages(self,
                      request: CreateMessagesRequest,
                      request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Create new localization messages
        
        Args:
            request: Messages to create with tenant context
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Created message records
        """
        request_info = request_info or RequestConfig.get_request_info()
        request.request_info = request_info
        
        payload = request.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_create",
            json_data=payload
        )

    def search_messages(self, request: LocaleRequest) -> Dict:
        """
        Search localized messages
        
        Args:
            request: Locale request parameters
            
        Returns:
            Dict: Matching localized messages
        """
        
        params = request.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_search",
            params=params
        )

    def update_messages(self,
                      request: UpdateMessageRequest,
                      request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Update existing localized messages
        
        Args:
            request: Update parameters with messages
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Update status and count
        """
        request_info = request_info or RequestConfig.get_request_info()
        request.request_info = request_info
        
        payload = request.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_update",
            json_data=payload
        )

    def delete_messages(self,
                      request: DeleteMessagesRequest,
                      request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Delete localized messages
        
        Args:
            request: Messages to delete
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Deletion status
        """
        request_info = request_info or RequestConfig.get_request_info()
        request.request_info = request_info
        
        payload = request.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_delete",
            json_data=payload
        )

    def upsert_messages(self,
                      request: CreateMessagesRequest,
                      request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Create or update localized messages
        
        Args:
            request: Messages to upsert
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Upsert operation results
        """
        request_info = request_info or RequestConfig.get_request_info()
        request.request_info = request_info
        
        payload = request.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_upsert",
            json_data=payload
        )
