from dataclasses import dataclass
from typing import Any, Optional
import re

@dataclass
class EncReqObject:
    """
    Model for encryption request object
    """
    tenant_id: str
    type: str
    value: Any

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.type:
            raise ValueError("type is required")
        if self.value is None:
            raise ValueError("value is required")

    def to_dict(self) -> dict:
        return {
            'tenantId': self.tenant_id,
            'type': self.type,
            'value': self.value
        }

@dataclass
class SignRequest:
    """
    Model for signing request
    """
    tenant_id: str
    value: str

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.value:
            raise ValueError("value is required")

    def to_dict(self) -> dict:
        return {
            'tenantId': self.tenant_id,
            'value': self.value
        }

class Signature:
    """
    Model for cryptographic signature
    """
    def __init__(self, signature_value: str):
        try:
            cipher_array = signature_value.split('|')
            if len(cipher_array) != 2:
                raise ValueError
            self.key_id = int(cipher_array[0])
            self.signature_value = cipher_array[1]
        except Exception as e:
            raise ValueError(f"{signature_value}: Invalid Signature") from e

    def __str__(self) -> str:
        return f"{self.key_id}|{self.signature_value}"

    def to_dict(self) -> dict:
        return {
            'keyId': self.key_id,
            'signatureValue': self.signature_value
        }

@dataclass
class VerifyRequest:
    """
    Model for verification request
    """
    value: str
    signature: Signature

    def __post_init__(self):
        if not self.value:
            raise ValueError("value is required")
        if not self.signature:
            raise ValueError("signature is required")

    def to_dict(self) -> dict:
        return {
            'value': self.value,
            'signature': str(self.signature)
        }

@dataclass
class RotateKeyRequest:
    """
    Model for key rotation request
    """
    tenant_id: str

    def __post_init__(self):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")

    def to_dict(self) -> dict:
        return {
            'tenantId': self.tenant_id
        }

# Builder classes
class EncReqObjectBuilder:
    def __init__(self):
        self._tenant_id = None
        self._type = None
        self._value = None

    def with_tenant_id(self, tenant_id: str) -> 'EncReqObjectBuilder':
        self._tenant_id = tenant_id
        return self

    def with_type(self, type: str) -> 'EncReqObjectBuilder':
        self._type = type
        return self

    def with_value(self, value: Any) -> 'EncReqObjectBuilder':
        self._value = value
        return self

    def build(self) -> EncReqObject:
        return EncReqObject(
            tenant_id=self._tenant_id,
            type=self._type,
            value=self._value
        )

class SignRequestBuilder:
    def __init__(self):
        self._tenant_id = None
        self._value = None

    def with_tenant_id(self, tenant_id: str) -> 'SignRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_value(self, value: str) -> 'SignRequestBuilder':
        self._value = value
        return self

    def build(self) -> SignRequest:
        return SignRequest(
            tenant_id=self._tenant_id,
            value=self._value
        )

class VerifyRequestBuilder:
    def __init__(self):
        self._value = None
        self._signature = None

    def with_value(self, value: str) -> 'VerifyRequestBuilder':
        self._value = value
        return self

    def with_signature(self, signature: Signature) -> 'VerifyRequestBuilder':
        self._signature = signature
        return self

    def build(self) -> VerifyRequest:
        return VerifyRequest(
            value=self._value,
            signature=self._signature
        )

class RotateKeyRequestBuilder:
    def __init__(self):
        self._tenant_id = None

    def with_tenant_id(self, tenant_id: str) -> 'RotateKeyRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def build(self) -> RotateKeyRequest:
        return RotateKeyRequest(
            tenant_id=self._tenant_id
        )
