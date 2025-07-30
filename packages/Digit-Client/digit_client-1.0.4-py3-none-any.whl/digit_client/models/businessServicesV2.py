from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .mdms_v2 import AuditDetails
from .workflow import State

@dataclass
class BusinessService:
    """
    Model for business service
    """
    tenant_id: str
    business_service: str
    business: str
    states: List[State]
    uuid: Optional[str] = None
    get_uri: Optional[str] = None
    post_uri: Optional[str] = None
    business_service_sla: Optional[int] = None
    audit_details: Optional[AuditDetails] = None

    def __post_init__(self):
        if not self.tenant_id or len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be between 1 and 256 characters")
        if self.uuid and len(self.uuid) > 256:
            raise ValueError("uuid must be at most 256 characters")
        if not self.business_service or len(self.business_service) > 256:
            raise ValueError("business_service must be between 1 and 256 characters")
        if not self.business or len(self.business) > 256:
            raise ValueError("business must be between 1 and 256 characters")
        if self.get_uri and len(self.get_uri) > 1024:
            raise ValueError("get_uri must be at most 1024 characters")
        if self.post_uri and len(self.post_uri) > 1024:
            raise ValueError("post_uri must be at most 1024 characters")
        if not self.states:
            raise ValueError("states is required")

    def add_states_item(self, states_item: State) -> 'BusinessService':
        if self.states is None:
            self.states = []
        self.states.append(states_item)
        return self

    def get_state_from_uuid(self, uuid: str) -> Optional[State]:
        """
        Returns the state with the given uuid if present, otherwise returns None
        """
        if self.states:
            for state in self.states:
                if state.uuid.lower() == uuid.lower():
                    return state
        return None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'tenantId': self.tenant_id,
            'businessService': self.business_service,
            'business': self.business,
            'states': [state.to_dict() for state in self.states]
        }
        if self.uuid:
            result['uuid'] = self.uuid
        if self.get_uri:
            result['getUri'] = self.get_uri
        if self.post_uri:
            result['postUri'] = self.post_uri
        if self.business_service_sla is not None:
            result['businessServiceSla'] = self.business_service_sla
        if self.audit_details:
            result['auditDetails'] = self.audit_details.to_dict()
        return result

@dataclass
class BusinessServiceSearchCriteria:
    """
    Model for business service search criteria
    """
    tenant_id: str
    business_services: Optional[List[str]] = None
    state_uuids: Optional[List[str]] = field(default=None, repr=False)
    action_uuids: Optional[List[str]] = field(default=None, repr=False)

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'tenantId': self.tenant_id
        }
        if self.business_services:
            result['businessServices'] = self.business_services
        if self.state_uuids:
            result['stateUuids'] = self.state_uuids
        if self.action_uuids:
            result['actionUuids'] = self.action_uuids
        return result

class BusinessServiceBuilder:
    """Builder class for creating BusinessService objects"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._uuid: Optional[str] = None
        self._business_service: Optional[str] = None
        self._business: Optional[str] = None
        self._get_uri: Optional[str] = None
        self._post_uri: Optional[str] = None
        self._business_service_sla: Optional[int] = None
        self._states: List[State] = []
        self._audit_details: Optional[AuditDetails] = None

    def with_tenant_id(self, tenant_id: str) -> 'BusinessServiceBuilder':
        self._tenant_id = tenant_id
        return self

    def with_uuid(self, uuid: str) -> 'BusinessServiceBuilder':
        self._uuid = uuid
        return self

    def with_business_service(self, business_service: str) -> 'BusinessServiceBuilder':
        self._business_service = business_service
        return self

    def with_business(self, business: str) -> 'BusinessServiceBuilder':
        self._business = business
        return self

    def with_get_uri(self, get_uri: str) -> 'BusinessServiceBuilder':
        self._get_uri = get_uri
        return self

    def with_post_uri(self, post_uri: str) -> 'BusinessServiceBuilder':
        self._post_uri = post_uri
        return self

    def with_business_service_sla(self, business_service_sla: int) -> 'BusinessServiceBuilder':
        self._business_service_sla = business_service_sla
        return self

    def with_states(self, states: List[State]) -> 'BusinessServiceBuilder':
        self._states = states
        return self

    def add_state(self, state: State) -> 'BusinessServiceBuilder':
        self._states.append(state)
        return self

    def with_audit_details(self, audit_details: AuditDetails) -> 'BusinessServiceBuilder':
        self._audit_details = audit_details
        return self

    def build(self) -> BusinessService:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._business_service:
            raise ValueError("business_service is required")
        if not self._business:
            raise ValueError("business is required")
        if not self._states:
            raise ValueError("states is required")
        
        return BusinessService(
            tenant_id=self._tenant_id,
            uuid=self._uuid,
            business_service=self._business_service,
            business=self._business,
            get_uri=self._get_uri,
            post_uri=self._post_uri,
            business_service_sla=self._business_service_sla,
            states=self._states,
            audit_details=self._audit_details
        )

class BusinessServiceSearchCriteriaBuilder:
    """Builder class for creating BusinessServiceSearchCriteria objects"""
    def __init__(self):
        self._tenant_id: Optional[str] = None
        self._business_services: Optional[List[str]] = None
        self._state_uuids: Optional[List[str]] = None
        self._action_uuids: Optional[List[str]] = None

    def with_tenant_id(self, tenant_id: str) -> 'BusinessServiceSearchCriteriaBuilder':
        self._tenant_id = tenant_id
        return self

    def with_business_services(self, business_services: List[str]) -> 'BusinessServiceSearchCriteriaBuilder':
        self._business_services = business_services
        return self

    def with_state_uuids(self, state_uuids: List[str]) -> 'BusinessServiceSearchCriteriaBuilder':
        self._state_uuids = state_uuids
        return self

    def with_action_uuids(self, action_uuids: List[str]) -> 'BusinessServiceSearchCriteriaBuilder':
        self._action_uuids = action_uuids
        return self

    def build(self) -> BusinessServiceSearchCriteria:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        
        return BusinessServiceSearchCriteria(
            tenant_id=self._tenant_id,
            business_services=self._business_services,
            state_uuids=self._state_uuids,
            action_uuids=self._action_uuids
        )
