from dataclasses import dataclass
from typing import Optional
from enum import Enum

class OtpRequestType(Enum):
    REGISTER = "register"
    LOGIN = "login"
    PASSWORD_RESET = "passwordreset"

@dataclass
class Otp:
    """
    Model for OTP verification
    """
    otp: Optional[str] = None
    uuid: Optional[str] = None  # Mapped to 'UUID' in JSON
    identity: Optional[str] = None
    tenant_id: Optional[str] = None
    validation_successful: bool = False

    def __post_init__(self):
        if self.otp and len(self.otp) > 128:
            raise ValueError("otp must be at most 128 characters")
        if self.uuid and len(self.uuid) > 36:
            raise ValueError("uuid must be at most 36 characters")
        if self.identity and len(self.identity) > 100:
            raise ValueError("identity must be at most 100 characters")
        if self.tenant_id and len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be at most 256 characters")

    def to_dict(self) -> dict:
        return {
            "otp": self.otp,
            "UUID": self.uuid,
            "identity": self.identity,
            "tenantId": self.tenant_id,
            "isValidationSuccessful": self.validation_successful
        }

@dataclass
class UserOtp:
    """
    Model for user OTP requests
    """
    mobile_number: Optional[str] = None
    tenant_id: Optional[str] = None
    type: Optional[str] = None  # Mapped to OtpRequestType
    user_type: Optional[str] = None

    def get_type_default(self) -> OtpRequestType:
        """Get mapped OtpRequestType with REGISTER default"""
        if not self.type:
            return OtpRequestType.REGISTER
        return self._map_to_domain_type()

    def _map_to_domain_type(self) -> Optional[OtpRequestType]:
        type_lower = self.type.lower() if self.type else ""
        return {
            "register": OtpRequestType.REGISTER,
            "login": OtpRequestType.LOGIN,
            "passwordreset": OtpRequestType.PASSWORD_RESET
        }.get(type_lower)

    def to_dict(self) -> dict:
        return {
            "mobileNumber": self.mobile_number,
            "tenantId": self.tenant_id,
            "type": self.type,
            "userType": self.user_type
        }

# Builder classes
class OtpBuilder:
    def __init__(self):
        self._otp = None
        self._uuid = None
        self._identity = None
        self._tenant_id = None
        self._validation_successful = False

    def with_otp(self, otp: str) -> 'OtpBuilder':
        self._otp = otp
        return self

    def with_uuid(self, uuid: str) -> 'OtpBuilder':
        self._uuid = uuid
        return self

    def with_identity(self, identity: str) -> 'OtpBuilder':
        self._identity = identity
        return self

    def with_tenant_id(self, tenant_id: str) -> 'OtpBuilder':
        self._tenant_id = tenant_id
        return self

    def with_validation_successful(self, success: bool) -> 'OtpBuilder':
        self._validation_successful = success
        return self

    def build(self) -> Otp:
        return Otp(
            otp=self._otp,
            uuid=self._uuid,
            identity=self._identity,
            tenant_id=self._tenant_id,
            validation_successful=self._validation_successful
        )

class UserOtpBuilder:
    def __init__(self):
        self._mobile_number = None
        self._tenant_id = None
        self._type = None
        self._user_type = None

    def with_mobile_number(self, number: str) -> 'UserOtpBuilder':
        self._mobile_number = number
        return self

    def with_tenant_id(self, tenant_id: str) -> 'UserOtpBuilder':
        self._tenant_id = tenant_id
        return self

    def with_type(self, req_type: str) -> 'UserOtpBuilder':
        self._type = req_type
        return self

    def with_user_type(self, user_type: str) -> 'UserOtpBuilder':
        self._user_type = user_type
        return self

    def build(self) -> UserOtp:
        return UserOtp(
            mobile_number=self._mobile_number,
            tenant_id=self._tenant_id,
            type=self._type,
            user_type=self._user_type
        )
