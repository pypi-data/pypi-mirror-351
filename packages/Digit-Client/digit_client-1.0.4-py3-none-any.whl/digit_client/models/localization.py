from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Any
from ..request_config import RequestInfo


@dataclass
class LocaleRequest:
    """
    Model for locale request parameters.
    """
    locale: str
    tenant_id: str
    module: Optional[str] = None
    codes: Optional[Set[str]] = None

    def __post_init__(self):
        if not self.locale:
            raise ValueError("locale is required")
        if not self.tenant_id or len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be at most 256 characters")

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "locale": self.locale,
            "tenantId": self.tenant_id,
        }
        if self.module:
            result["module"] = self.module
        if self.codes:
            result["codes"] = list(self.codes)
        return result


@dataclass
class Message:
    """
    Model for individual messages.
    """
    code: str
    message: str
    module: str
    locale: str

    def __post_init__(self):
        if not self.code:
            raise ValueError("code is required")
        if not self.message:
            raise ValueError("message is required")
        if not self.module:
            raise ValueError("module is required")
        if not self.locale:
            raise ValueError("locale is required")

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "module": self.module,
            "locale": self.locale,
        }


@dataclass
class CreateMessagesRequest:
    """
    Model for creating messages request.
    """
    tenant_id: str
    messages: List[Message]
    request_info: RequestInfo=field(default_factory=RequestInfo)

    def __post_init__(self):
        if not self.tenant_id or len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be at most 256 characters")
        if not self.messages or len(self.messages) < 1:
            raise ValueError("messages must contain at least one item")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RequestInfo": self.request_info.to_dict(),
            "tenantId": self.tenant_id,
            "messages": [message.to_dict() for message in self.messages],
        }

@dataclass
class UpdateMessage:
    """
    Model for individual update messages.
    """
    code: str
    message: str

    def __post_init__(self):
        if not self.code:
            raise ValueError("code is required")
        if not self.message:
            raise ValueError("message is required")

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
        }

@dataclass
class UpdateMessageRequest:
    """
    Model for updating messages request.
    """
    tenant_id: str
    locale: str
    module: str
    messages: List[UpdateMessage]
    request_info: RequestInfo=field(default_factory=RequestInfo)

    def __post_init__(self):
        if not self.tenant_id or len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be at most 256 characters")
        if not self.locale or len(self.locale) > 255:
            raise ValueError("locale must be at most 255 characters")
        if not self.module or len(self.module) > 255:
            raise ValueError("module must be at most 255 characters")
        if not self.messages or len(self.messages) < 1:
            raise ValueError("messages must contain at least one item")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RequestInfo": self.request_info.to_dict(),
            "tenantId": self.tenant_id,
            "locale": self.locale,
            "module": self.module,
            "messages": [message.to_dict() for message in self.messages],
        }




# Builder Classes

class LocaleRequestBuilder:
    """Builder class for creating LocaleRequest objects."""
    
    def __init__(self):
        self._locale = None
        self._tenant_id = None
        self._module = None
        self._codes = None

    def with_locale(self, locale: str) -> 'LocaleRequestBuilder':
        self._locale = locale
        return self

    def with_tenant_id(self, tenant_id: str) -> 'LocaleRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_module(self, module: str) -> 'LocaleRequestBuilder':
        self._module = module
        return self

    def with_codes(self, codes: Set[str]) -> 'LocaleRequestBuilder':
        self._codes = codes
        return self

    def build(self) -> LocaleRequest:
        return LocaleRequest(
            locale=self._locale,
            tenant_id=self._tenant_id,
            module=self._module,
            codes=self._codes,
        )


class CreateMessagesRequestBuilder:
    """Builder class for creating CreateMessagesRequest objects."""
    
    def __init__(self):
        self._request_info = None
        self._tenant_id = None
        self._messages = []

    # def with_request_info(self, request_info: RequestInfo) -> 'CreateMessagesRequestBuilder':
    #     self._request_info = request_info
    #     return self

    def with_tenant_id(self, tenant_id: str) -> 'CreateMessagesRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def add_message(self, message: Message) -> 'CreateMessagesRequestBuilder':
        self._messages.append(message)
        return self

    def build(self) -> CreateMessagesRequest:
        return CreateMessagesRequest(
            request_info=self._request_info,
            tenant_id=self._tenant_id,
            messages=self._messages,
        )


class UpdateMessageRequestBuilder:
    """Builder class for creating UpdateMessageRequest objects."""
    
    def __init__(self):
        self._request_info = None
        self._tenant_id = None
        self._locale = None
        self._module = None
        self._messages = []

    # def with_request_info(self, request_info: RequestInfo) -> 'UpdateMessageRequestBuilder':
    #     self._request_info = request_info
    #     return self

    def with_tenant_id(self, tenant_id: str) -> 'UpdateMessageRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def with_locale(self, locale: str) -> 'UpdateMessageRequestBuilder':
        self._locale = locale
        return self

    def with_module(self, module: str) -> 'UpdateMessageRequestBuilder':
        self._module = module
        return self

    def add_message(self, message: UpdateMessage) -> 'UpdateMessageRequestBuilder':
        self._messages.append(message)
        return self

    def build(self) -> UpdateMessageRequest:
        return UpdateMessageRequest(
            request_info=self._request_info,
            tenant_id=self._tenant_id,
            locale=self._locale,
            module=self._module,
            messages=self._messages,
        )
       
class MessageBuilder:
    """Builder class for creating Message objects."""
    def __init__(self):
        self._code = None
        self._message = None
        self._module = None
        self._locale = None

    def with_code(self, code: str) -> 'MessageBuilder': 
        self._code = code
        return self

    def with_message(self, message: str) -> 'MessageBuilder':
        self._message = message
        return self

    def with_module(self, module: str) -> 'MessageBuilder':
        self._module = module
        return self

    def with_locale(self, locale: str) -> 'MessageBuilder':
        self._locale = locale
        return self

    def build(self) -> Message:
        return Message(
            code=self._code,
            message=self._message,
            module=self._module,
            locale=self._locale
        )

class UpdateMessageBuilder:
    """Builder class for creating UpdateMessage objects."""
    def __init__(self):
        self._code = None
        self._message = None    

    def with_code(self, code: str) -> 'UpdateMessageBuilder':
        self._code = code
        return self

    def with_message(self, message: str) -> 'UpdateMessageBuilder':
        self._message = message
        return self

    def build(self) -> UpdateMessage:
        return UpdateMessage(
            code=self._code,
            message=self._message
        )   

@dataclass
class DeleteMessage:
    """
    Model for message deletion parameters
    """
    code: str
    module: str
    locale: str

    def __post_init__(self):
        if not self.code:
            raise ValueError("code is required")
        if not self.module:
            raise ValueError("module is required")
        if not self.locale:
            raise ValueError("locale is required")

    def to_dict(self) -> Dict[str, str]:
        return {
            "code": self.code,
            "module": self.module,
            "locale": self.locale
        }

@dataclass
class DeleteMessagesRequest:
    """
    Model for bulk message deletion request
    """
    tenant_id: str
    messages: List[DeleteMessage]
    request_info: RequestInfo=field(default_factory=RequestInfo)

    def __post_init__(self):
        if not self.tenant_id or len(self.tenant_id) > 256:
            raise ValueError("tenant_id must be 1-256 characters")
        if not self.messages or len(self.messages) < 1:
            raise ValueError("messages must contain at least one item")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RequestInfo": self.request_info.to_dict(),
            "tenantId": self.tenant_id,
            "messages": [msg.to_dict() for msg in self.messages]
        }

# Builder classes
class DeleteMessageBuilder:
    """Builder for DeleteMessage objects"""
    def __init__(self):
        self._code = None
        self._module = None
        self._locale = None

    def with_code(self, code: str) -> 'DeleteMessageBuilder':
        self._code = code
        return self

    def with_module(self, module: str) -> 'DeleteMessageBuilder':
        self._module = module
        return self

    def with_locale(self, locale: str) -> 'DeleteMessageBuilder':
        self._locale = locale
        return self

    def build(self) -> DeleteMessage:
        return DeleteMessage(
            code=self._code,
            module=self._module,
            locale=self._locale
        )

class DeleteMessagesRequestBuilder:
    """Builder for DeleteMessagesRequest objects"""
    def __init__(self):
        self._request_info = None
        self._tenant_id = None
        self._messages = []

    # def with_request_info(self, request_info: RequestInfo) -> 'DeleteMessagesRequestBuilder':
    #     self._request_info = request_info
    #     return self

    def with_tenant_id(self, tenant_id: str) -> 'DeleteMessagesRequestBuilder':
        self._tenant_id = tenant_id
        return self

    def add_message(self, message: DeleteMessage) -> 'DeleteMessagesRequestBuilder':
        self._messages.append(message)
        return self

    def build(self) -> DeleteMessagesRequest:
        if not self._tenant_id:
            raise ValueError("tenant_id is required")
        if not self._messages:
            raise ValueError("at least one message is required")
            
        return DeleteMessagesRequest(
            request_info=self._request_info,
            tenant_id=self._tenant_id,
            messages=self._messages
        )