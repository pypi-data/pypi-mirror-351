from typing import List, Dict, Any, Optional
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.Report import MetadataRequest, ReportRequest

class ReportService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "report"

    def create_v1_metadata(self,
                    module_name: str,
                    version: str,
                    request: MetadataRequest,
                    request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Get metadata for a report - corresponds to /{moduleName}/{version}/metadata/_get endpoint
        
        Args:
            module_name: Name of the module from URI
            request: Metadata request object containing requestInfo, tenantId, and reportName
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Metadata response
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = request.to_dict()
        payload["RequestInfo"] = request_info.to_dict()

        return self.api_client.post(
            f"{self.base_url}/{module_name}/{version}/metadata/_get",
            json_data=payload
        )

    def get_report_data_v1(self,
                       module_name: str,
                       version: str,
                       request: ReportRequest,
                       request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Get report data - corresponds to /{moduleName}/{version}/_get endpoint
        
        Args:
            module_name: Name of the module from URI
            request: Report request object containing requestInfo, tenantId, reportName and searchParams
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Report data response
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = request.to_dict()
        payload["RequestInfo"] = request_info.to_dict()

        return self.api_client.post(
            f"{self.base_url}/{module_name}/{version}/_get",
            json_data=payload
        )
