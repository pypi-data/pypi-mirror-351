from typing import Dict, List, Optional, Any
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.filestore import (
    FileUploadRequest, FileUploadRequestBuilder,
    FileRetrieveByIdRequest, FileRetrieveByIdRequestBuilder,
    FileRetrieveByTagRequest, FileRetrieveByTagRequestBuilder,
    FileRetrieveByUrlRequest, FileRetrieveByUrlRequestBuilder
)

class FileStoreService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "filestore/v1/files"

    def upload_files(self,
                    file_upload_request: FileUploadRequest) -> Dict:
        """
        Upload multiple files to the server
        
        Args:
            file_upload_request: FileUploadRequest object containing upload parameters
            
        Returns:
            Dict: Response containing uploaded file details
        """
        # Get form data from request object
        form_data = file_upload_request.to_dict()
            
        # Add files to form data
        files_data = []
        for file_obj in file_upload_request.files:
            files_data.append(("file", file_obj))
            
        return self.api_client.post(
            self.base_url,
            data=form_data,
            files=files_data
        )
        
    def get_file_by_id(self,
                      file_retrieve_by_id_request: FileRetrieveByIdRequest) -> bytes:
        """
        Download a file by its fileStoreId
        
        Args:
            tenant_id: Tenant identifier
            file_store_id: Unique file identifier
            
        Returns:
            bytes: File content as bytes
        """
            
        return self.api_client.get(
            f"{self.base_url}/id",
            params=file_retrieve_by_id_request.to_dict(),
            stream=True  # Stream the response to handle large files
        )
        
    def get_file_metadata(self,
                         file_retrieve_by__request: FileRetrieveByIdRequest) -> Dict:
        """
        Get metadata for a file
        
        Args:
            tenant_id: Tenant identifier
            file_store_id: Unique file identifier
            
        Returns:
            Dict: File metadata
        """

        return self.api_client.get(
            f"{self.base_url}/metadata",
            params=file_retrieve_by__request.to_dict()
        )
        
    def get_file_urls(self,
                     file_retrieve_by_url_request: FileRetrieveByUrlRequest) -> Dict:
        """
        Get URLs for multiple files
        
        Args:
            tenant_id: Tenant identifier
            file_store_ids: List of file identifiers
            
        Returns:
            Dict: Response containing file IDs and their URLs
        """
            
        return self.api_client.get(
            f"{self.base_url}/url",
            params=file_retrieve_by_url_request.to_dict()
        )
        
    def get_files_by_tag(self,
                        file_retrieve_by_tag_request: FileRetrieveByTagRequest) -> Dict:
        """
        Get files associated with a specific tag
        
        Args:
            tenant_id: Tenant identifier
            tag: Tag to filter files
            
        Returns:
            Dict: Files associated with the tag
        """

        return self.api_client.get(
            f"{self.base_url}/tag",
            params=file_retrieve_by_tag_request.to_dict()
        )
