from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from ..request_config import RequestInfo

@dataclass
class BoundarySearchRequest:
    """
    Model for boundary search request parameters
    """
    tenant_id: str
    boundary_ids: Optional[List[int]] = None
    boundary_num: Optional[List[int]] = None
    boundary_type: Optional[str] = None
    hierarchy_type: Optional[str] = None
    codes: Optional[List[str]] = None

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be at most 256 characters")
        if self.boundary_type and len(self.boundary_type) > 64:
            raise ValueError("boundary_type must be at most 64 characters")
        if self.hierarchy_type and len(self.hierarchy_type) > 128:
            raise ValueError("hierarchy_type must be at most 128 characters")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'tenantId': self.tenant_id
        }
        if self.boundary_ids:
            result['boundaryIds'] = self.boundary_ids
        if self.boundary_num:
            result['boundaryNum'] = self.boundary_num
        if self.boundary_type:
            result['boundaryType'] = self.boundary_type
        if self.hierarchy_type:
            result['hierarchyType'] = self.hierarchy_type
        if self.codes:
            result['codes'] = self.codes
        return result

@dataclass
class LocationBoundarySearchRequest:
    """
    Model for boundary type search request parameters
    """
    tenant_id: str
    request_info: RequestInfo
    hierarchy_type_code: Optional[str] = None
    codes: Optional[List[str]] = None
    boundary_type: Optional[str] = None

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be at most 256 characters")
        if self.hierarchy_type_code and len(self.hierarchy_type_code) > 128:
            raise ValueError("hierarchy_type_code must be at most 128 characters")
        if self.boundary_type and len(self.boundary_type) > 64:
            raise ValueError("boundary_type must be at most 64 characters")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'tenantId': self.tenant_id,
            'RequestInfo': self.request_info.to_dict()
        }
        if self.hierarchy_type_code:
            result['hierarchyTypeCode'] = self.hierarchy_type_code
        if self.codes:
            result['codes'] = self.codes
        if self.boundary_type:
            result['boundaryType'] = self.boundary_type
        return result

class BoundarySearchRequestBuilder:
    """Builder class for creating BoundarySearchRequest objects"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._boundary_ids: Optional[List[int]] = None
        self._boundary_num: Optional[List[int]] = None
        self._boundary_type: Optional[str] = None
        self._hierarchy_type: Optional[str] = None
        self._codes: Optional[List[str]] = None

    def with_tenant_id(self, tenant_id: str) -> 'BoundarySearchRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_boundary_ids(self, boundary_ids: List[int]) -> 'BoundarySearchRequestBuilder':
        self._boundary_ids = boundary_ids
        return self

    def with_boundary_num(self, boundary_num: List[int]) -> 'BoundarySearchRequestBuilder':
        self._boundary_num = boundary_num
        return self

    def with_boundary_type(self, boundary_type: str) -> 'BoundarySearchRequestBuilder':
        self._boundary_type = boundary_type
        return self

    def with_hierarchy_type(self, hierarchy_type: str) -> 'BoundarySearchRequestBuilder':
        self._hierarchy_type = hierarchy_type
        return self

    def with_codes(self, codes: List[str]) -> 'BoundarySearchRequestBuilder':
        self._codes = codes
        return self

    def build(self) -> BoundarySearchRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        
        return BoundarySearchRequest(
            tenant_id=self._tenant_id,
            boundary_ids=self._boundary_ids,
            boundary_num=self._boundary_num,
            boundary_type=self._boundary_type,
            hierarchy_type=self._hierarchy_type,
            codes=self._codes
        )

class LocationBoundarySearchRequestBuilder:
    """Builder class for creating BoundaryTypeSearchRequest objects"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._request_info: Optional[RequestInfo] = None
        self._hierarchy_type_code: Optional[str] = None
        self._codes: Optional[List[str]] = None
        self._boundary_type: Optional[str] = None

    def with_tenant_id(self, tenant_id: str) -> 'LocationBoundarySearchRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_request_info(self, request_info: RequestInfo) -> 'LocationBoundarySearchRequestBuilder':
        self._request_info = request_info
        return self

    def with_hierarchy_type_code(self, hierarchy_type_code: str) -> 'LocationBoundarySearchRequestBuilder':
        self._hierarchy_type_code = hierarchy_type_code
        return self

    def with_codes(self, codes: List[str]) -> 'LocationBoundarySearchRequestBuilder':
        self._codes = codes
        return self

    def with_boundary_type(self, boundary_type: str) -> 'LocationBoundarySearchRequestBuilder':
        self._boundary_type = boundary_type
        return self

    def build(self) -> LocationBoundarySearchRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._request_info:
            raise ValueError("request_info is required")
        
        return LocationBoundarySearchRequest(
            tenant_id=self._tenant_id,
            request_info=self._request_info,
            hierarchy_type_code=self._hierarchy_type_code,
            codes=self._codes,
            boundary_type=self._boundary_type
        )
