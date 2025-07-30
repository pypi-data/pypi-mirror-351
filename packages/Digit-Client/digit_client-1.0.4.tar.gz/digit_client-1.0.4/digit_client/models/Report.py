from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from ..request_config import RequestInfo


@dataclass
class MetadataRequest:
    """
    Model for Metadata Request
    """
    request_info: RequestInfo
    tenant_id: str
    report_name: str

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.report_name:
            raise ValueError("report_name is required")

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.request_info:
            result["requestInfo"] = self.request_info.to_dict()
        if self.tenant_id:
            result["tenantId"] = self.tenant_id
        if self.report_name:
            result["reportName"] = self.report_name
        return result


@dataclass
class SearchParam:
    """
    Model for Search Parameters
    """
    input: Any

    def to_dict(self) -> Dict[str, Any]:
        return {"input": self.input}


@dataclass
class ReportRequest(MetadataRequest):
    """
    Model for Report Request extending MetadataRequest
    """
    search_params: List[SearchParam] = field(default_factory=list)

    def add_search_param(self, search_param: SearchParam) -> 'ReportRequest':
        self.search_params.append(search_param)
        return self

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict["searchParams"] = [param.to_dict() for param in self.search_params]
        return base_dict


# Builder Classes

class MetadataRequestBuilder:
    """Builder class for creating MetadataRequest objects"""
    def __init__(self):
        self._request_info = None
        self._tenant_id = None
        self._report_name = None


    def with_tenant_id(self, tenant_id: str) -> 'MetadataRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_report_name(self, report_name: str) -> 'MetadataRequestBuilder':
        self._report_name = report_name
        return self

    def build(self) -> MetadataRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._report_name:
            raise ValueError("report_name is required")

        return MetadataRequest(
            request_info=self._request_info,
            tenant_id=self._tenant_id,
            report_name=self._report_name,
        )


class SearchParamBuilder:
    """Builder class for creating SearchParam objects"""
    def __init__(self):
        self._input = None

    def with_input(self, input: Any) -> 'SearchParamBuilder':
        self._input = input
        return self

    def build(self) -> SearchParam:
        return SearchParam(input=self._input)


class ReportRequestBuilder(MetadataRequestBuilder):
    """Builder class for creating ReportRequest objects"""
    def __init__(self):
        super().__init__()
        self._search_params = []

    def add_search_param(self, search_param: SearchParam) -> 'ReportRequestBuilder':
        self._search_params.append(search_param)
        return self

    def build(self) -> ReportRequest:
        metadata_request = super().build()
        
        return ReportRequest(
            request_info=metadata_request.request_info,
            tenant_id=metadata_request.tenant_id,
            report_name=metadata_request.report_name,
            search_params=self._search_params,
        )
