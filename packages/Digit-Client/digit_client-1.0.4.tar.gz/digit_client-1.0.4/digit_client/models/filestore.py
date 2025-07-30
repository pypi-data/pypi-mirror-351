from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage  # For MultipartFile equivalent in Python

@dataclass
class FileUploadRequest:
    """
    Model for file upload request parameters
    """
    files: List[FileStorage]
    tenant_id: str
    module: str
    tag: Optional[str] = None
    request_info: Optional[str] = None

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.module:
            raise ValueError("module is required")
        if not self.files:
            raise ValueError("files are required")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'tenantId': self.tenant_id,
            'module': self.module,
            
        }
        result['files'] = [file.filename for file in self.files]
        if self.tag:
            result['tag'] = self.tag
        if self.request_info:
            result['requestInfo'] = self.request_info
        # Files cannot be converted to dict directly
        return result

@dataclass
class FileRetrieveByIdRequest:
    """
    Model for file retrieval by ID request parameters
    """
    tenant_id: str
    file_store_id: str

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.file_store_id:
            raise ValueError("file_store_id is required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tenantId': self.tenant_id,
            'fileStoreId': self.file_store_id
        }

@dataclass
class FileRetrieveByUrlRequest:
    """
    Model for file retrieval by multiple URLs request parameters
    """
    tenant_id: str
    file_store_ids: List[str]

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.file_store_ids:
            raise ValueError("file_store_ids are required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tenantId': self.tenant_id,
            'fileStoreIds': self.file_store_ids
        }

@dataclass
class FileRetrieveByTagRequest:
    """
    Model for file retrieval by tag request parameters
    """
    tenant_id: str
    tag: str

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.tag:
            raise ValueError("tag is required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tenantId': self.tenant_id,
            'tag': self.tag
        }

# Builder classes
class FileUploadRequestBuilder:
    """Builder class for creating FileUploadRequest objects"""
    def __init__(self):
        self._files: List[FileStorage] = []
        self._tenant_id: Optional[str] = None
        self._module: Optional[str] = None
        self._tag: Optional[str] = None
        self._request_info: Optional[str] = None

    def with_files(self, files: List[FileStorage]) -> 'FileUploadRequestBuilder':
        self._files = files
        return self

    def add_file(self, file: FileStorage) -> 'FileUploadRequestBuilder':
        self._files.append(file)
        return self

    def with_tenant_id(self, tenant_id: str) -> 'FileUploadRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_module(self, module: str) -> 'FileUploadRequestBuilder':
        self._module = module
        return self

    def with_tag(self, tag: str) -> 'FileUploadRequestBuilder':
        self._tag = tag
        return self

    def with_request_info(self, request_info: str) -> 'FileUploadRequestBuilder':
        self._request_info = request_info
        return self

    def build(self) -> FileUploadRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._module:
            raise ValueError("module is required")
        if not self._files:
            raise ValueError("files are required")
        
        return FileUploadRequest(
            files=self._files,
            tenant_id=self._tenant_id,
            module=self._module,
            tag=self._tag,
            request_info=self._request_info
        )

class FileRetrieveByIdRequestBuilder:
    """Builder class for creating FileRetrieveByIdRequest objects"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._file_store_id: Optional[str] = None

    def with_tenant_id(self, tenant_id: str) -> 'FileRetrieveByIdRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_file_store_id(self, file_store_id: str) -> 'FileRetrieveByIdRequestBuilder':
        self._file_store_id = file_store_id
        return self

    def build(self) -> FileRetrieveByIdRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._file_store_id:
            raise ValueError("file_store_id is required")
        
        return FileRetrieveByIdRequest(
            tenant_id=self._tenant_id,
            file_store_id=self._file_store_id
        )

class FileRetrieveByUrlRequestBuilder:
    """Builder class for creating FileRetrieveByUrlRequest objects"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._file_store_ids: List[str] = []

    def with_tenant_id(self, tenant_id: str) -> 'FileRetrieveByUrlRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_file_store_ids(self, file_store_ids: List[str]) -> 'FileRetrieveByUrlRequestBuilder':
        self._file_store_ids = file_store_ids
        return self

    def add_file_store_id(self, file_store_id: str) -> 'FileRetrieveByUrlRequestBuilder':
        self._file_store_ids.append(file_store_id)
        return self

    def build(self) -> FileRetrieveByUrlRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._file_store_ids:
            raise ValueError("file_store_ids are required")
        
        return FileRetrieveByUrlRequest(
            tenant_id=self._tenant_id,
            file_store_ids=self._file_store_ids
        )

class FileRetrieveByTagRequestBuilder:
    """Builder class for creating FileRetrieveByTagRequest objects"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._tag: Optional[str] = None

    def with_tenant_id(self, tenant_id: str) -> 'FileRetrieveByTagRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_tag(self, tag: str) -> 'FileRetrieveByTagRequestBuilder':
        self._tag = tag
        return self

    def build(self) -> FileRetrieveByTagRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._tag:
            raise ValueError("tag is required")
        
        return FileRetrieveByTagRequest(
            tenant_id=self._tenant_id,
            tag=self._tag
        )
