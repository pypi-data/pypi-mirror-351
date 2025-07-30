from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from .mdms_v2 import AuditDetails

@dataclass
class AttributeValue:
    """
    Model for attribute values
    """
    attribute_code: str
    value: Any
    id: Optional[str] = None
    reference_id: Optional[str] = None
    audit_details: Optional[AuditDetails] = None
    additional_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.attribute_code:
            raise ValueError("attribute_code is required")
        if self.reference_id and (len(self.reference_id) < 2 or len(self.reference_id) > 64):
            raise ValueError("reference_id must be between 2-64 characters")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "attributeCode": self.attribute_code,
            "value": self.value
        }
        if self.id:
            result["id"] = self.id
        if self.reference_id:
            result["referenceId"] = self.reference_id
        if self.audit_details:
            result["auditDetails"] = self.audit_details.to_dict()
        if self.additional_details:
            result["additionalDetails"] = self.additional_details
        return result

@dataclass
class Service:
    """
    Model for service definition
    """
    tenant_id: str
    service_def_id: str
    account_id: str
    attributes: List[AttributeValue]
    id: Optional[str] = None
    reference_id: Optional[str] = None
    client_id: Optional[str] = None
    audit_details: Optional[AuditDetails] = None
    additional_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if len(self.tenant_id) < 2 or len(self.tenant_id) > 64:
            raise ValueError("tenant_id must be between 2-64 characters")
        if len(self.service_def_id) < 2 or len(self.service_def_id) > 64:
            raise ValueError("service_def_id must be between 2-64 characters")
        if self.reference_id and (len(self.reference_id) < 2 or len(self.reference_id) > 64):
            raise ValueError("reference_id must be between 2-64 characters")
        if self.client_id and len(self.client_id) > 64:
            raise ValueError("client_id must be at most 64 characters")
        if not self.attributes:
            raise ValueError("attributes cannot be empty")

    def add_attribute(self, attribute: AttributeValue) -> 'Service':
        self.attributes.append(attribute)
        return self

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "tenantId": self.tenant_id,
            "serviceDefId": self.service_def_id,
            "accountId": self.account_id,
            "attributes": [attr.to_dict() for attr in self.attributes]
        }
        if self.id:
            result["id"] = self.id
        if self.reference_id:
            result["referenceId"] = self.reference_id
        if self.client_id:
            result["clientId"] = self.client_id
        if self.audit_details:
            result["auditDetails"] = self.audit_details.to_dict()
        if self.additional_details:
            result["additionalDetails"] = self.additional_details
        return result

@dataclass
class ServiceCriteria:
    """
    Model for service search criteria
    """
    tenant_id: str
    ids: Optional[List[str]] = None
    service_def_ids: Optional[List[str]] = None
    reference_ids: Optional[List[str]] = None
    account_id: Optional[str] = None
    client_id: Optional[str] = None

    def __post_init__(self):
        if len(self.tenant_id) < 2 or len(self.tenant_id) > 64:
            raise ValueError("tenant_id must be between 2-64 characters")

    def add_id(self, id: str) -> 'ServiceCriteria':
        if not self.ids:
            self.ids = []
        self.ids.append(id)
        return self

    def add_service_def_id(self, service_def_id: str) -> 'ServiceCriteria':
        if not self.service_def_ids:
            self.service_def_ids = []
        self.service_def_ids.append(service_def_id)
        return self

    def add_reference_id(self, reference_id: str) -> 'ServiceCriteria':
        if not self.reference_ids:
            self.reference_ids = []
        self.reference_ids.append(reference_id)
        return self

    def to_dict(self) -> Dict[str, Any]:
        result = {"tenantId": self.tenant_id}
        if self.ids:
            result["ids"] = self.ids
        if self.service_def_ids:
            result["serviceDefIds"] = self.service_def_ids
        if self.reference_ids:
            result["referenceIds"] = self.reference_ids
        if self.account_id:
            result["accountId"] = self.account_id
        if self.client_id:
            result["clientId"] = self.client_id
        return result

class OrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"

@dataclass
class Pagination:
    """
    Model for pagination parameters
    """
    limit: int = 10
    offset: int = 0
    total_count: Optional[int] = None
    sort_by: Optional[str] = None
    order: OrderEnum = OrderEnum.ASC

    def __post_init__(self):
        if self.limit < 1:
            raise ValueError("limit must be at least 1")
        if self.offset < 0:
            raise ValueError("offset cannot be negative")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "limit": self.limit,
            "offset": self.offset,
            "totalCount": self.total_count,
            "sortBy": self.sort_by,
            "order": self.order.value
        }

# Builder classes
class AttributeValueBuilder:
    def __init__(self):
        self._attribute_code = None
        self._value = None
        self._id = None
        self._reference_id = None
        self._audit_details = None
        self._additional_details = None

    def with_attribute_code(self, code: str) -> 'AttributeValueBuilder':
        self._attribute_code = code
        return self

    def with_value(self, value: Any) -> 'AttributeValueBuilder':
        self._value = value
        return self
    def with_id(self, id: str) -> 'AttributeValueBuilder':
        self._id = id
        return self

    def with_reference_id(self, ref_id: str) -> 'AttributeValueBuilder':
        self._reference_id = ref_id
        return self
    def with_audit_details(self, audit_details: AuditDetails) -> 'AttributeValueBuilder':
        self._audit_details = audit_details
        return self
    def with_additional_details(self, additional_details: Dict[str, Any]) -> 'AttributeValueBuilder':
        self._additional_details = additional_details
        return self

    def build(self) -> AttributeValue:
        return AttributeValue(
            attribute_code=self._attribute_code,
            value=self._value,
            id=self._id,
            reference_id=self._reference_id,
            audit_details=self._audit_details,
            additional_details=self._additional_details
        )

class ServiceBuilder:
    def __init__(self):
        self._tenant_id = None
        self._service_def_id = None
        self._account_id = None
        self._attributes = []
        self._reference_id = None
        self._client_id = None
        self._audit_details = None
        self._additional_details = None

    def with_tenant_id(self, tenant_id: str) -> 'ServiceBuilder':
        self._tenant_id = tenant_id
        return self

    def with_service_def_id(self, service_def_id: str) -> 'ServiceBuilder':
        self._service_def_id = service_def_id
        return self

    def with_account_id(self, account_id: str) -> 'ServiceBuilder':
        self._account_id = account_id
        return self

    def add_attribute(self, attribute: AttributeValue) -> 'ServiceBuilder':
        self._attributes.append(attribute)
        return self

    def with_reference_id(self, reference_id: str) -> 'ServiceBuilder':
        self._reference_id = reference_id
        return self

    def with_client_id(self, client_id: str) -> 'ServiceBuilder':
        self._client_id = client_id
        return self

    def with_audit_details(self, audit_details: AuditDetails) -> 'ServiceBuilder':
        self._audit_details = audit_details
        return self 

    def with_additional_details(self, additional_details: Dict[str, Any]) -> 'ServiceBuilder':
        self._additional_details = additional_details
        return self

    def build(self) -> Service:
        return Service(
            tenant_id=self._tenant_id,
            service_def_id=self._service_def_id,
            account_id=self._account_id,
            attributes=self._attributes,
            reference_id=self._reference_id,
            client_id=self._client_id,
            audit_details=self._audit_details,
            additional_details=self._additional_details
        )

class ServiceCriteriaBuilder:
    def __init__(self):
        self._tenant_id = None
        self._ids = None
        self._service_def_ids = None
        self._reference_ids = None
        self._account_id = None
        self._client_id = None

    def with_tenant_id(self, tenant_id: str) -> 'ServiceCriteriaBuilder':
        self._tenant_id = tenant_id
        return self

    def with_ids(self, ids: List[str]) -> 'ServiceCriteriaBuilder':
        self._ids = ids
        return self
    def add_id(self, id: str) -> 'ServiceCriteriaBuilder':
        if self._ids is None:
            self._ids = []
        self._ids.append(id)
        return self
    def with_service_def_ids(self, service_def_ids: List[str]) -> 'ServiceCriteriaBuilder':
        self._service_def_ids = service_def_ids
        return self
    def add_service_def_id(self, service_def_id: str) -> 'ServiceCriteriaBuilder':
        if self._service_def_ids is None:
            self._service_def_ids = []
        self._service_def_ids.append(service_def_id)
        return self 
    def with_reference_ids(self, reference_ids: List[str]) -> 'ServiceCriteriaBuilder':
        self._reference_ids = reference_ids
        return self
    def add_reference_id(self, reference_id: str) -> 'ServiceCriteriaBuilder':
        if self._reference_ids is None:
            self._reference_ids = []
        self._reference_ids.append(reference_id)
        return self
    def with_account_id(self, account_id: str) -> 'ServiceCriteriaBuilder':
        self._account_id = account_id
        return self
    def with_client_id(self, client_id: str) -> 'ServiceCriteriaBuilder':
        self._client_id = client_id
        return self
    
    def build(self) -> ServiceCriteria:
        return ServiceCriteria(
            tenant_id=self._tenant_id,
            ids=self._ids,
            service_def_ids=self._service_def_ids,
            reference_ids=self._reference_ids,
            account_id=self._account_id,
            client_id=self._client_id
        )

class PaginationBuilder:
    def __init__(self):
        self._limit = 10
        self._offset = 0
        self._total_count = None
        self._sort_by = None
        self._order = OrderEnum.ASC

    def with_limit(self, limit: int) -> 'PaginationBuilder':
        self._limit = limit
        return self
    def with_offset(self, offset: int) -> 'PaginationBuilder':
        self._offset = offset
        return self 
    def with_total_count(self, total_count: int) -> 'PaginationBuilder':
        self._total_count = total_count
        return self
    def with_sort_by(self, sort_by: str) -> 'PaginationBuilder':
        self._sort_by = sort_by
        return self
    def with_order(self, order: OrderEnum) -> 'PaginationBuilder':
        self._order = order
        return self
    def build(self) -> Pagination:
        return Pagination(
            limit=self._limit,
            offset=self._offset,
            total_count=self._total_count,
            sort_by=self._sort_by,
            order=self._order
        )
        
class DataTypeEnum(str, Enum):
    STRING = "String"
    NUMBER = "Number"
    TEXT = "Text"
    DATETIME = "Datetime"
    SINGLEVALUELIST = "SingleValueList"
    MULTIVALUELIST = "MultiValueList"
    FILE = "File"

    @classmethod
    def from_value(cls, value: str) -> Optional['DataTypeEnum']:
        for member in cls:
            if member.value == value:
                return member
        return None

@dataclass
class AttributeDefinition:
    code: str
    data_type: DataTypeEnum
    id: Optional[str] = None
    reference_id: Optional[str] = None
    tenant_id: Optional[str] = None
    values: Optional[List[str]] = None
    is_active: bool = True
    required: Optional[bool] = None
    regex: Optional[str] = None
    order: Optional[str] = None
    audit_details: Optional[AuditDetails] = None
    additional_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        for field in [self.id, self.reference_id, self.tenant_id, self.regex]:
            if field and (len(field) < 2 or len(field) > 64):
                raise ValueError("Field must be between 2-64 characters")
        if not self.code or len(self.code) < 2 or len(self.code) > 64:
            raise ValueError("code must be 2-64 characters")

    def add_values_item(self, value: str) -> 'AttributeDefinition':
        if not self.values:
            self.values = []
        self.values.append(value)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "dataType": self.data_type.value,
            "id": self.id,
            "referenceId": self.reference_id,
            "tenantId": self.tenant_id,
            "values": self.values,
            "isActive": self.is_active,
            "required": self.required,
            "regex": self.regex,
            "order": self.order,
            "auditDetails": self.audit_details.to_dict() if self.audit_details else None,
            "additionalDetails": self.additional_details
        }

@dataclass
class ServiceDefinition:
    code: str
    tenant_id: str
    attributes: List[AttributeDefinition]
    id: Optional[str] = None
    is_active: bool = True
    client_id: Optional[str] = None
    audit_details: Optional[AuditDetails] = None
    additional_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        for field in [self.id, self.tenant_id, self.code, self.client_id]:
            if field and (len(field) < 2 or len(field) > 64):
                raise ValueError("Field must be between 2-64 characters")
        if not self.attributes:
            raise ValueError("attributes cannot be empty")

    def add_attribute(self, attribute: AttributeDefinition) -> 'ServiceDefinition':
        self.attributes.append(attribute)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tenantId": self.tenant_id,
            "code": self.code,
            "isActive": self.is_active,
            "attributes": [attr.to_dict() for attr in self.attributes],
            "clientId": self.client_id,
            "auditDetails": self.audit_details.to_dict() if self.audit_details else None,
            "additionalDetails": self.additional_details
        }

@dataclass
class ServiceDefinitionCriteria:
    tenant_id: str
    ids: Optional[List[str]] = None
    codes: Optional[List[str]] = None
    client_id: Optional[str] = None

    def __post_init__(self):
        if len(self.tenant_id) < 2 or len(self.tenant_id) > 64:
            raise ValueError("tenant_id must be 2-64 characters")

    def add_id(self, id: str) -> 'ServiceDefinitionCriteria':
        if not self.ids:
            self.ids = []
        self.ids.append(id)
        return self

    def add_code(self, code: str) -> 'ServiceDefinitionCriteria':
        if not self.codes:
            self.codes = []
        self.codes.append(code)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenantId": self.tenant_id,
            "ids": self.ids,
            "code": self.codes,
            "clientId": self.client_id
        }

# Builder Classes
class AttributeDefinitionBuilder:
    def __init__(self):
        self._code = None
        self._data_type = None
        self._values = []
        self._id = None
        self._reference_id = None
        self._tenant_id = None
        self._is_active = True
        self._required = None
        self._regex = None
        self._order = None
        self._audit_details = None
        self._additional_details = None

    def with_code(self, code: str) -> 'AttributeDefinitionBuilder':
        self._code = code
        return self

    def with_data_type(self, data_type: DataTypeEnum) -> 'AttributeDefinitionBuilder':
        self._data_type = data_type
        return self

    def add_value(self, value: str) -> 'AttributeDefinitionBuilder':
        self._values.append(value)
        return self
    def with_id(self, id: str) -> 'AttributeDefinitionBuilder':
        self._id = id
        return self
    def with_reference_id(self, reference_id: str) -> 'AttributeDefinitionBuilder':
        self._reference_id = reference_id
        return self
    def with_tenant_id(self, tenant_id: str) -> 'AttributeDefinitionBuilder':
        self._tenant_id = tenant_id
        return self
    def with_is_active(self, is_active: bool) -> 'AttributeDefinitionBuilder':
        self._is_active = is_active
        return self 
    def with_required(self, required: bool) -> 'AttributeDefinitionBuilder':
        self._required = required
        return self
    def with_regex(self, regex: str) -> 'AttributeDefinitionBuilder':
        self._regex = regex
        return self 
    def with_order(self, order: str) -> 'AttributeDefinitionBuilder':
        self._order = order
        return self
    def with_audit_details(self, audit_details: AuditDetails) -> 'AttributeDefinitionBuilder':
        self._audit_details = audit_details
        return self 
    def with_additional_details(self, additional_details: Dict[str, Any]) -> 'AttributeDefinitionBuilder':
        self._additional_details = additional_details
        return self 

    def build(self) -> AttributeDefinition:
        attr = AttributeDefinition(
            code=self._code,
            data_type=self._data_type,
            values=self._values if self._values else None,
            id=self._id,
            reference_id=self._reference_id,
            tenant_id=self._tenant_id,
            is_active=self._is_active,
            required=self._required,
            regex=self._regex,
            order=self._order,
            audit_details=self._audit_details,
            additional_details=self._additional_details
        )
        return attr

class ServiceDefinitionBuilder:
    def __init__(self):
        self._code = None
        self._tenant_id = None
        self._attributes = []
        self._id = None
        self._is_active = True
        self._client_id = None
        self._audit_details = None
        self._additional_details = None         

    def with_code(self, code: str) -> 'ServiceDefinitionBuilder':
        self._code = code
        return self

    def with_tenant_id(self, tenant_id: str) -> 'ServiceDefinitionBuilder':
        self._tenant_id = tenant_id
        return self

    def add_attribute(self, attribute: AttributeDefinition) -> 'ServiceDefinitionBuilder':
        self._attributes.append(attribute)
        return self
    def with_id(self, id: str) -> 'ServiceDefinitionBuilder':
        self._id = id
        return self
    def with_is_active(self, is_active: bool) -> 'ServiceDefinitionBuilder':
        self._is_active = is_active
        return self 
    def with_client_id(self, client_id: str) -> 'ServiceDefinitionBuilder': 
        self._client_id = client_id
        return self 
    def with_audit_details(self, audit_details: AuditDetails) -> 'ServiceDefinitionBuilder':
        self._audit_details = audit_details
        return self  
    def with_additional_details(self, additional_details: Dict[str, Any]) -> 'ServiceDefinitionBuilder':
        self._additional_details = additional_details   
        return self 
    def build(self) -> ServiceDefinition:
        return ServiceDefinition(
            code=self._code,
            tenant_id=self._tenant_id,
            attributes=self._attributes,
            id=self._id,
            is_active=self._is_active,
            client_id=self._client_id,
            audit_details=self._audit_details,
            additional_details=self._additional_details
        )

class ServiceDefinitionCriteriaBuilder:
    def __init__(self):
        self._tenant_id = None
        self._ids = None
        self._codes = None
        self._client_id = None


    def with_tenant_id(self, tenant_id: str) -> 'ServiceDefinitionCriteriaBuilder':
        self._tenant_id = tenant_id
        return self

    def with_ids(self, ids: List[str]) -> 'ServiceDefinitionCriteriaBuilder':
        self._ids = ids
        return self
    def add_id(self, id: str) -> 'ServiceDefinitionCriteriaBuilder':
        if self._ids is None:
            self._ids = []
        self._ids.append(id)
        return self
    
    def with_codes(self, codes: List[str]) -> 'ServiceDefinitionCriteriaBuilder':
        self._codes = codes
        return self
    def add_code(self, code: str) -> 'ServiceDefinitionCriteriaBuilder':
        if self._codes is None:
            self._codes = []
        self._codes.append(code)
        return self 
    def with_client_id(self, client_id: str) -> 'ServiceDefinitionCriteriaBuilder':
        self._client_id = client_id
        return self 
    def build(self) -> ServiceDefinitionCriteria:
        return ServiceDefinitionCriteria(
            tenant_id=self._tenant_id,
            ids=self._ids,
            codes=self._codes,
            client_id=self._client_id
        )
