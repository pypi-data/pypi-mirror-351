from typing import List, Dict, Optional
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.ServiceRequest import (
    ServiceDefinition, ServiceDefinitionCriteria,
    Service, ServiceCriteria, Pagination,
    AttributeDefinition, DataTypeEnum, OrderEnum
)

class ServiceRequestService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "service-request/service"

    def create_service_definition(self,
                                definition: ServiceDefinition,
                                request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Create a new service definition with attributes
        
        Args:
            definition: Service definition structure
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Created service definition
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "serviceDefinition": definition.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/definition/v1/_create",
            json_data=payload
        )

    def search_service_definitions(self,
                                 criteria: ServiceDefinitionCriteria,
                                 pagination: Pagination,
                                 request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Search service definitions
        
        Args:
            criteria: Filters for service definitions
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Matching service definitions
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "serviceDefinitionCriteria": criteria.to_dict(),
            "pagination": pagination.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/definition/v1/_search",
            json_data=payload
        )

    def create_service(self,
                     service: Service,
                     request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Create a new service request
        
        Args:
            service: Service request details
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Created service request
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "Service": service.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/v1/_create",
            json_data=payload
        )

    def search_services(self,
                      criteria: ServiceCriteria,
                      pagination: Pagination,
                      request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Search service requests with pagination
        
        Args:
            criteria: Filters for service requests
            pagination: Page size and offset
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Paginated service request results
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "ServiceCriteria": criteria.to_dict(),
            "Pagination": pagination.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/v1/_search",
            json_data=payload
        )
