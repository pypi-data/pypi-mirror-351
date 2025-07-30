from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..request_config import RequestInfo

@dataclass
class PaginationDetails:
    offset_key: str
    size_key: str
    max_page_size: int
    starting_offset: int = 0
    max_records: int = 0

    def __post_init__(self):
        if not self.offset_key:
            raise ValueError("offset_key is required")
        if not self.size_key:
            raise ValueError("size_key is required")
        if self.max_page_size <= 0:
            raise ValueError("max_page_size must be positive")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "offsetKey": self.offset_key,
            "sizeKey": self.size_key,
            "maxPageSize": self.max_page_size,
            "startingOffset": self.starting_offset,
            "maxRecords": self.max_records
        }

@dataclass
class APIDetails:
    uri: str
    pagination_details: PaginationDetails
    response_json_path: str
    request: Optional[Dict[str, Any]] = None
    tenant_id_for_open_search: Optional[str] = None
    custom_query_param: Optional[str] = None

    def __post_init__(self):
        if not self.uri:
            raise ValueError("uri is required")
        if not self.response_json_path:
            raise ValueError("response_json_path is required")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "uri": self.uri,
            "paginationDetails": self.pagination_details.to_dict(),
            "responseJsonPath": self.response_json_path
        }
        if self.request:
            result["request"] = self.request
        if self.tenant_id_for_open_search:
            result["tenantIdForOpenSearch"] = self.tenant_id_for_open_search
        if self.custom_query_param:
            result["customQueryParam"] = self.custom_query_param
        return result

@dataclass
class ReindexRequest:
    request_info: RequestInfo
    index: str
    type: str
    reindex_topic: str
    tenant_id: str
    batch_size: Optional[int] = None
    job_id: Optional[str] = None
    start_time: Optional[int] = None
    total_records: Optional[int] = None

    def __post_init__(self):
        if not self.index:
            raise ValueError("index is required")
        if not self.type:
            raise ValueError("type is required")
        if not self.reindex_topic:
            raise ValueError("reindex_topic is required")
        if not self.tenant_id:
            raise ValueError("tenant_id is required")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "RequestInfo": self.request_info.to_dict(),
            "index": self.index,
            "type": self.type,
            "reindexTopic": self.reindex_topic,
            "tenantId": self.tenant_id
        }
        if self.batch_size:
            result["batchSize"] = self.batch_size
        if self.job_id:
            result["jobId"] = self.job_id
        if self.start_time:
            result["startTime"] = self.start_time
        if self.total_records:
            result["totalRecords"] = self.total_records
        return result

@dataclass
class LegacyIndexRequest:
    request_info: RequestInfo
    api_details: APIDetails
    legacy_index_topic: str
    tenant_id: str
    job_id: Optional[str] = None
    start_time: Optional[int] = None
    total_records: Optional[int] = None

    def __post_init__(self):
        if not self.legacy_index_topic:
            raise ValueError("legacy_index_topic is required")
        if not self.tenant_id:
            raise ValueError("tenant_id is required")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "RequestInfo": self.request_info.to_dict(),
            "apiDetails": self.api_details.to_dict(),
            "legacyIndexTopic": self.legacy_index_topic,
            "tenantId": self.tenant_id
        }
        if self.job_id:
            result["jobId"] = self.job_id
        if self.start_time:
            result["startTime"] = self.start_time
        if self.total_records:
            result["totalRecords"] = self.total_records
        return result

# Builder classes
class PaginationDetailsBuilder:
    def __init__(self):
        self._offset_key = None
        self._size_key = None
        self._max_page_size = None
        self._starting_offset = 0
        self._max_records = 0

    def with_offset_key(self, key: str) -> 'PaginationDetailsBuilder':
        self._offset_key = key
        return self

    def with_size_key(self, key: str) -> 'PaginationDetailsBuilder':
        self._size_key = key
        return self

    def with_max_page_size(self, size: int) -> 'PaginationDetailsBuilder':
        self._max_page_size = size
        return self

    def with_starting_offset(self, offset: int) -> 'PaginationDetailsBuilder':
        self._starting_offset = offset
        return self

    def with_max_records(self, records: int) -> 'PaginationDetailsBuilder':
        self._max_records = records
        return self

    def build(self) -> PaginationDetails:
        return PaginationDetails(
            offset_key=self._offset_key,
            size_key=self._size_key,
            max_page_size=self._max_page_size,
            starting_offset=self._starting_offset,
            max_records=self._max_records
        )

class APIDetailsBuilder:
    def __init__(self):
        self._uri = None
        self._pagination_details = None
        self._response_json_path = None
        self._request = None
        self._tenant_id_for_open_search = None
        self._custom_query_param = None

    def with_uri(self, uri: str) -> 'APIDetailsBuilder':
        self._uri = uri
        return self

    def with_pagination_details(self, details: PaginationDetails) -> 'APIDetailsBuilder':
        self._pagination_details = details
        return self

    def with_response_json_path(self, path: str) -> 'APIDetailsBuilder':
        self._response_json_path = path
        return self

    def with_request(self, request: Dict[str, Any]) -> 'APIDetailsBuilder':
        self._request = request
        return self

    def with_tenant_id_for_open_search(self, tenant_id: str) -> 'APIDetailsBuilder':
        self._tenant_id_for_open_search = tenant_id
        return self

    def with_custom_query_param(self, param: str) -> 'APIDetailsBuilder':
        self._custom_query_param = param
        return self

    def build(self) -> APIDetails:
        return APIDetails(
            uri=self._uri,
            pagination_details=self._pagination_details,
            response_json_path=self._response_json_path,
            request=self._request,
            tenant_id_for_open_search=self._tenant_id_for_open_search,
            custom_query_param=self._custom_query_param
        )

class ReindexRequestBuilder:
    def __init__(self):
        self._request_info = None
        self._index = None
        self._type = None
        self._reindex_topic = None
        self._tenant_id = None
        self._batch_size = None
        self._job_id = None
        self._start_time = None
        self._total_records = None

    # Builder methods for each field...
    def with_request_info(self, request_info: RequestInfo) -> 'ReindexRequestBuilder':
        self._request_info = request_info
        return self 
    
    def with_index(self, index: str) -> 'ReindexRequestBuilder':
        self._index = index
        return self
    
    def with_type(self, type: str) -> 'ReindexRequestBuilder':
        self._type = type
        return self
    
    def with_reindex_topic(self, reindex_topic: str) -> 'ReindexRequestBuilder':
        self._reindex_topic = reindex_topic
        return self
    
    def with_tenant_id(self, tenant_id: str) -> 'ReindexRequestBuilder':
        self._tenant_id = tenant_id
        return self
    
    def with_batch_size(self, batch_size: int) -> 'ReindexRequestBuilder':
        self._batch_size = batch_size
        return self 
    
    def with_job_id(self, job_id: str) -> 'ReindexRequestBuilder':
        self._job_id = job_id
        return self 
    
    def with_start_time(self, start_time: int) -> 'ReindexRequestBuilder':
        self._start_time = start_time
        return self 
    
    def with_total_records(self, total_records: int) -> 'ReindexRequestBuilder':
        self._total_records = total_records
        return self 
    
    def build(self) -> ReindexRequest:
        return ReindexRequest(
            request_info=self._request_info,
            index=self._index,
            type=self._type,
            reindex_topic=self._reindex_topic,
            tenant_id=self._tenant_id,
            batch_size=self._batch_size,
            job_id=self._job_id,
            start_time=self._start_time,
            total_records=self._total_records
        )

class LegacyIndexRequestBuilder:
    def __init__(self):
        self._request_info = None
        self._api_details = None
        self._legacy_index_topic = None
        self._tenant_id = None
        self._job_id = None
        self._start_time = None
        self._total_records = None

    # Builder methods for each field...
    def with_request_info(self, request_info: RequestInfo) -> 'LegacyIndexRequestBuilder':
        self._request_info = request_info
        return self
    
    def with_api_details(self, api_details: APIDetails) -> 'LegacyIndexRequestBuilder':
        self._api_details = api_details
        return self 
    
    def with_legacy_index_topic(self, legacy_index_topic: str) -> 'LegacyIndexRequestBuilder':
        self._legacy_index_topic = legacy_index_topic
        return self  
    
    def with_tenant_id(self, tenant_id: str) -> 'LegacyIndexRequestBuilder':
        self._tenant_id = tenant_id
        return self 
    
    def with_job_id(self, job_id: str) -> 'LegacyIndexRequestBuilder':
        self._job_id = job_id
        return self  
    
    def with_start_time(self, start_time: int) -> 'LegacyIndexRequestBuilder':
        self._start_time = start_time
        return self  
    
    def with_total_records(self, total_records: int) -> 'LegacyIndexRequestBuilder':
        self._total_records = total_records
        return self 
    
    def build(self) -> LegacyIndexRequest:
        return LegacyIndexRequest(  
            request_info=self._request_info,
            api_details=self._api_details,
            legacy_index_topic=self._legacy_index_topic,
            tenant_id=self._tenant_id,
            job_id=self._job_id,
            start_time=self._start_time,    
            total_records=self._total_records
        )
