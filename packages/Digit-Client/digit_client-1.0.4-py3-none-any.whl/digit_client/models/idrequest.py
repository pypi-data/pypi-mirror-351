from dataclasses import dataclass
from typing import Optional

@dataclass
class IdRequest:
    """
    Model for ID request parameters
    """
    id_name: str
    tenant_id: str
    format: Optional[str] = None
    count: Optional[int] = None

    def __post_init__(self):
        if not self.id_name or len(self.id_name) > 200:
            raise ValueError("id_name must be between 1 and 200 characters")
        if not self.tenant_id or len(self.tenant_id) > 200:
            raise ValueError("tenant_id must be between 1 and 200 characters")
        if self.format and len(self.format) > 200:
            raise ValueError("format must be at most 200 characters")

    def to_dict(self) -> dict:
        result = {
            'idName': self.id_name,
            'tenantId': self.tenant_id
        }
        if self.format:
            result['format'] = self.format
        if self.count is not None:
            result['count'] = self.count
        return result

class IdRequestBuilder:
    """Builder class for creating IdRequest objects"""
    def __init__(self):
        self._id_name: Optional[str] = None
        self._tenant_id: Optional[str] = None
        self._format: Optional[str] = None
        self._count: Optional[int] = None

    def with_id_name(self, id_name: str) -> 'IdRequestBuilder':
        self._id_name = id_name
        return self

    def with_tenant_id(self, tenant_id: str) -> 'IdRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_format(self, format: str) -> 'IdRequestBuilder':
        self._format = format
        return self

    def with_count(self, count: int) -> 'IdRequestBuilder':
        self._count = count
        return self

    def build(self) -> IdRequest:
        if not self._id_name:
            raise ValueError("id_name is required")
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        
        return IdRequest(
            id_name=self._id_name,
            tenant_id=self._tenant_id,
            format=self._format,
            count=self._count
        )
