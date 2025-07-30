from typing import Dict, Any, Optional
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.Indexer import (
    LegacyIndexRequest, 
    ReindexRequest,
    LegacyIndexRequestBuilder,
    ReindexRequestBuilder,
    APIDetails,
    APIDetailsBuilder,
    PaginationDetails,
    PaginationDetailsBuilder
)

class IndexerService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "index-operations"

    def legacy_index(self,
                   request: LegacyIndexRequest,
                   request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Perform legacy indexing operation
        
        Args:
            request: Legacy index configuration parameters
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Legacy indexing operation status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = request.to_dict()
        payload["RequestInfo"] = request_info.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_legacyindex",
            json_data=payload
        )

    def index_to_topic(self,
                     topic: str,
                     index_data: Dict[str, Any],
                     request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Index data to specific topic
        
        Args:
            topic: Target topic name (e.g., "finance-adoption-topic")
            index_data: JSON data to index
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Indexing operation status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "indexJson": index_data
        }

        return self.api_client.post(
            f"{self.base_url}/{topic}/_index",
            json_data=payload
        )

    def reindex_data(self,
                   request: ReindexRequest,
                   request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Reindex data between indices
        
        Args:
            request: Reindex configuration parameters
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Reindexing operation status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = request.to_dict()
        payload["RequestInfo"] = request_info.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_reindex",
            json_data=payload
        )
