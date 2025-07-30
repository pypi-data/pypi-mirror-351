from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class UserSearchModel:
    """Model for user search criteria"""
    tenantId: str
    id: Optional[List[int]] = None
    uuid: Optional[List[str]] = None
    userName: Optional[str] = None
    name: Optional[str] = None
    mobileNumber: Optional[str] = None
    aadhaarNumber: Optional[str] = None
    pan: Optional[str] = None
    emailId: Optional[str] = None
    fuzzyLogic: Optional[bool] = None
    active: Optional[bool] = None
    pageSize: Optional[int] = None
    pageNumber: Optional[int] = 0
    sort: Optional[List[str]] = field(default_factory=lambda: ["name"])
    userType: Optional[str] = None
    roleCodes: Optional[List[str]] = None
    
    def to_dict(self) -> dict:
        """Convert the search model to a dictionary for API request"""
        search_dict = {
            "tenantId": self.tenantId
        }
        
        if self.id is not None:
            search_dict["id"] = self.id
            
        if self.uuid is not None:
            search_dict["uuid"] = self.uuid
            
        if self.userName is not None:
            search_dict["userName"] = self.userName
            
        if self.name is not None:
            search_dict["name"] = self.name
            
        if self.mobileNumber is not None:
            search_dict["mobileNumber"] = self.mobileNumber
            
        if self.aadhaarNumber is not None:
            search_dict["aadhaarNumber"] = self.aadhaarNumber
            
        if self.pan is not None:
            search_dict["pan"] = self.pan
            
        if self.emailId is not None:
            search_dict["emailId"] = self.emailId
            
        if self.fuzzyLogic is not None:
            search_dict["fuzzyLogic"] = str(self.fuzzyLogic).lower()
            
        if self.active is not None:
            search_dict["active"] = str(self.active).lower()
            
        if self.pageSize is not None:
            search_dict["pageSize"] = self.pageSize
            
        if self.pageNumber is not None:
            search_dict["pageNumber"] = self.pageNumber
            
        if self.sort is not None:
            search_dict["sort"] = self.sort
            
        if self.userType is not None:
            search_dict["userType"] = self.userType
            
        if self.roleCodes is not None:
            search_dict["roleCodes"] = self.roleCodes
            
        return search_dict
    
class UserSearchModelBuilder:
    def __init__(self):
        self._tenant_id = None
        self._id = None
        self._uuid = None
        self._user_name = None
        self._name = None
        self._mobile_number = None
        self._aadhaar_number = None
        self._pan = None
        self._email_id = None
        self._fuzzy_logic = None
        self._active = None
        self._page_size = None
        self._page_number = 0
        self._sort = ["name"]
        self._user_type = None
        self._role_codes = None
        
    def with_tenant_id(self, tenant_id: str) -> 'UserSearchModelBuilder':
        self._tenant_id = tenant_id
        return self
    
    def with_id(self, id: List[int]) -> 'UserSearchModelBuilder':
        self._id = id
        return self
    
    def with_uuid(self, uuid: List[str]) -> 'UserSearchModelBuilder':
        self._uuid = uuid
        return self
        
    def with_user_name(self, user_name: str) -> 'UserSearchModelBuilder':
        self._user_name = user_name
        return self
        
    def with_name(self, name: str) -> 'UserSearchModelBuilder':
        self._name = name
        return self
        
    def with_mobile_number(self, mobile_number: str) -> 'UserSearchModelBuilder':
        self._mobile_number = mobile_number
        return self
        
    def with_aadhaar_number(self, aadhaar_number: str) -> 'UserSearchModelBuilder':
        self._aadhaar_number = aadhaar_number
        return self
        
    def with_pan(self, pan: str) -> 'UserSearchModelBuilder':
        self._pan = pan
        return self
        
    def with_email_id(self, email_id: str) -> 'UserSearchModelBuilder':
        self._email_id = email_id
        return self
        
    def with_fuzzy_logic(self, fuzzy_logic: bool) -> 'UserSearchModelBuilder':
        self._fuzzy_logic = fuzzy_logic
        return self
        
    def with_active(self, active: bool) -> 'UserSearchModelBuilder':
        self._active = active
        return self
        
    def with_page_size(self, page_size: int) -> 'UserSearchModelBuilder':
        self._page_size = page_size
        return self
        
    def with_page_number(self, page_number: int) -> 'UserSearchModelBuilder':
        self._page_number = page_number
        return self
        
    def with_sort(self, sort: List[str]) -> 'UserSearchModelBuilder':
        self._sort = sort
        return self
        
    def with_user_type(self, user_type: str) -> 'UserSearchModelBuilder':
        self._user_type = user_type
        return self
        
    def with_role_codes(self, role_codes: List[str]) -> 'UserSearchModelBuilder':
        self._role_codes = role_codes
        return self
    
    def build(self) -> UserSearchModel:
        return UserSearchModel(
            tenantId=self._tenant_id,
            id=self._id,
            uuid=self._uuid,
            userName=self._user_name,
            name=self._name,
            mobileNumber=self._mobile_number,
            aadhaarNumber=self._aadhaar_number,
            pan=self._pan,
            emailId=self._email_id,
            fuzzyLogic=self._fuzzy_logic,
            active=self._active,
            pageSize=self._page_size,
            pageNumber=self._page_number,
            sort=self._sort,
            userType=self._user_type,
            roleCodes=self._role_codes
        )
 
        
