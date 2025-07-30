from typing import Dict, List, Optional, Any
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.pdf_service import PDFCreateRequest, PDFSearchCriteria, BulkPDFRequest

class PDFService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "pdf-service/v1"

    def create_pdf(self,
                 pdf_request: PDFCreateRequest,
                 request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Generate and store PDF documents
        
        Args:
            pdf_request: PDF configuration and data
            request_info: Authentication and request metadata
            
        Returns:
            Dict: PDF creation job details
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "Transaction": pdf_request.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_create",
            json_data=payload
        )

    def create_pdf_no_save(self,
                         pdf_request: PDFCreateRequest,
                         request_info: Optional[RequestInfo] = None) -> bytes:
        """
        Generate PDF without persistent storage
        
        Args:
            pdf_request: PDF configuration and data
            request_info: Authentication and request metadata
            
        Returns:
            bytes: PDF file content
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "Transaction": pdf_request.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_createnosave",
            json_data=payload,
            return_raw=True
        )

    def search_pdfs(self,
                  criteria: PDFSearchCriteria,
                  request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Search generated PDF documents
        
        Args:
            criteria: Search filters and parameters
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Matching PDF records
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_search",
            json_data=payload,
            params=criteria.to_dict()
        )

    def get_unregistered_codes(self,
                             request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Retrieve unregistered localization codes
        
        Args:
            request_info: Authentication and request metadata
            
        Returns:
            Dict: List of unregistered codes
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_getUnrigesteredCodes",
            json_data=payload
        )

    def clear_unregistered_codes(self,
                               request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Clear unregistered localization codes cache
        
        Args:
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Operation status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_clearUnrigesteredCodes",
            json_data=payload
        )

    def create_bulk_pdf(self,
                      bulk_request: BulkPDFRequest,
                      request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Initiate bulk PDF generation process
        
        Args:
            bulk_request: Bulk PDF configuration
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Bulk job details
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "BulkPDFRequest": bulk_request.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_createBulk",
            json_data=payload
        )

    def cancel_bulk_process(self,
                          job_id: str,
                          request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Cancel ongoing bulk PDF generation
        
        Args:
            job_id: Bulk job identifier
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Cancellation status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_cancelProcess",
            json_data=payload,
            params={"jobId": job_id}
        )
