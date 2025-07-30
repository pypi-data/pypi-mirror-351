from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum
from ..request_config import RequestInfo
from .user import User
from .mdms_v2 import AuditDetails

class TxnStatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"

    @classmethod
    def from_value(cls, value: str) -> Optional['TxnStatusEnum']:
        for status in cls:
            if status.value == value:
                return status
        return None

@dataclass
class TaxAndPayment:
    tax_amount: Decimal
    amount_paid: Decimal
    bill_id: str

    def __post_init__(self):
        if self.tax_amount < 0:
            raise ValueError("tax_amount cannot be negative")
        if self.amount_paid < 0:
            raise ValueError("amount_paid cannot be negative")
        if not self.bill_id:
            raise ValueError("bill_id is required")

@dataclass
class Transaction:
    tenant_id: str
    txn_amount: str
    bill_id: str
    consumer_code: str
    tax_and_payments: List[TaxAndPayment]
    product_info: str
    gateway: str
    callback_url: str
    user: User
    module: Optional[str] = None
    txn_id: Optional[str] = None
    redirect_url: Optional[str] = None
    txn_status: Optional[TxnStatusEnum] = None
    txn_status_msg: Optional[str] = None
    gateway_txn_id: Optional[str] = None
    gateway_payment_mode: Optional[str] = None
    gateway_status_code: Optional[str] = None
    gateway_status_msg: Optional[str] = None
    receipt: Optional[str] = None
    audit_details: Optional[AuditDetails] = None
    additional_details: Optional[Dict[str, Any]] = None
    response_json: Optional[Dict[str, Any]] = field(default=None, repr=False)
    additional_fields: Optional[Dict[str, Any]] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        if len(self.tenant_id) < 2 or len(self.tenant_id) > 50:
            raise ValueError("tenant_id must be between 2-50 characters")
        if not self.txn_amount:
            raise ValueError("txn_amount is required")
        if not self.bill_id:
            raise ValueError("bill_id is required")
        if not self.consumer_code or len(self.consumer_code) > 128:
            raise ValueError("consumer_code must be 1-128 characters")
        if not self.product_info or len(self.product_info) > 512:
            raise ValueError("product_info must be 1-512 characters")
        if not self.gateway:
            raise ValueError("gateway is required")
        if not self.callback_url:
            raise ValueError("callback_url is required")
        if not self.tax_and_payments:
            raise ValueError("tax_and_payments cannot be empty")
            
    def to_dict(self) -> dict:
        result = {}
        if self.tenant_id is not None:
            result["tenantId"] = self.tenant_id
        if self.txn_amount is not None:
            result["txnAmount"] = str(self.txn_amount) if isinstance(self.txn_amount, Decimal) else self.txn_amount
        if self.bill_id is not None:
            result["billId"] = self.bill_id
        if self.consumer_code is not None:
            result["consumerCode"] = self.consumer_code
        if self.tax_and_payments is not None:
            result["taxAndPayments"] = [{
                "taxAmount": str(payment.tax_amount) if isinstance(payment.tax_amount, Decimal) else payment.tax_amount,
                "amountPaid": str(payment.amount_paid) if isinstance(payment.amount_paid, Decimal) else payment.amount_paid,
                "billId": payment.bill_id
            } for payment in self.tax_and_payments]
        if self.product_info is not None:
            result["productInfo"] = self.product_info
        if self.gateway is not None:
            result["gateway"] = self.gateway
        if self.callback_url is not None:
            result["callbackUrl"] = self.callback_url
        if self.user is not None:
            result["user"] = self.user.to_dict()
        if self.module is not None:
            result["module"] = self.module
        if self.txn_id is not None:
            result["txnId"] = self.txn_id
        if self.redirect_url is not None:
            result["redirectUrl"] = self.redirect_url
        if self.txn_status is not None:
            result["txnStatus"] = self.txn_status.value
        if self.txn_status_msg is not None:
            result["txnStatusMsg"] = self.txn_status_msg
        if self.gateway_txn_id is not None:
            result["gatewayTxnId"] = self.gateway_txn_id
        if self.gateway_payment_mode is not None:
            result["gatewayPaymentMode"] = self.gateway_payment_mode
        if self.gateway_status_code is not None:
            result["gatewayStatusCode"] = self.gateway_status_code
        if self.gateway_status_msg is not None:
            result["gatewayStatusMsg"] = self.gateway_status_msg
        if self.receipt is not None:
            result["receipt"] = self.receipt
        if self.audit_details is not None:
            result["auditDetails"] = self.audit_details.__dict__
        if self.additional_details is not None:
            result["additionalDetails"] = self.additional_details
        if self.additional_fields is not None:
            result.update(self.additional_fields)
            
        return result

@dataclass
class TransactionCriteria:
    tenant_id: Optional[str] = None
    txn_id: Optional[str] = None
    bill_id: Optional[str] = None
    user_uuid: Optional[str] = None
    receipt: Optional[str] = None
    consumer_code: Optional[str] = None
    created_time: Optional[int] = field(default=None, repr=False)
    txn_status: Optional[TxnStatusEnum] = None
    limit: int = field(default=10, repr=False)
    offset: int = field(default=0, repr=False)
    
    def to_dict(self) -> dict:
        result = {}
        if self.tenant_id is not None:
            result["tenantId"] = self.tenant_id
        if self.txn_id is not None:
            result["txnId"] = self.txn_id
        if self.bill_id is not None:
            result["billId"] = self.bill_id
        if self.user_uuid is not None:
            result["userUuid"] = self.user_uuid
        if self.receipt is not None:
            result["receipt"] = self.receipt
        if self.consumer_code is not None:
            result["consumerCode"] = self.consumer_code
        if self.created_time is not None:
            result["createdTime"] = self.created_time
        if self.txn_status is not None:
            result["txnStatus"] = self.txn_status.value
        if self.limit is not None:
            result["limit"] = self.limit
        if self.offset is not None:
            result["offset"] = self.offset
            
        return result

# Builder classes
class TaxAndPaymentBuilder:
    def __init__(self):
        self._tax_amount = None
        self._amount_paid = None
        self._bill_id = None

    def with_tax_amount(self, amount: Decimal) -> 'TaxAndPaymentBuilder':
        self._tax_amount = amount
        return self

    def with_amount_paid(self, amount: Decimal) -> 'TaxAndPaymentBuilder':
        self._amount_paid = amount
        return self

    def with_bill_id(self, bill_id: str) -> 'TaxAndPaymentBuilder':
        self._bill_id = bill_id
        return self

    def build(self) -> TaxAndPayment:
        return TaxAndPayment(
            tax_amount=self._tax_amount,
            amount_paid=self._amount_paid,
            bill_id=self._bill_id
        )

class TransactionBuilder:
    def __init__(self):
        self._tenant_id = None
        self._txn_amount = None
        self._bill_id = None
        self._module = None
        self._consumer_code = None
        self._tax_and_payments = []
        self._product_info = None
        self._gateway = None
        self._callback_url = None
        self._user = None
        self._audit_details = None
        self._additional_details = None
        self._additional_fields = None
        self._response_json = None
        self._gateway_txn_id = None
        self._gateway_payment_mode = None
        self._gateway_status_code = None
        self._gateway_status_msg = None
        self._receipt = None
        self._txn_status = None
        self._txn_status_msg = None
        self._redirect_url = None
        self._txn_id = None

    def with_tenant_id(self, tenant_id: str) -> 'TransactionBuilder':
        self._tenant_id = tenant_id
        return self

    def with_txn_amount(self, amount: str) -> 'TransactionBuilder':
        self._txn_amount = amount
        return self

    def with_bill_id(self, bill_id: str) -> 'TransactionBuilder':
        self._bill_id = bill_id
        return self

    def with_consumer_code(self, code: str) -> 'TransactionBuilder':
        self._consumer_code = code
        return self

    def add_tax_payment(self, payment: TaxAndPayment) -> 'TransactionBuilder':
        self._tax_and_payments.append(payment)
        return self

    def with_product_info(self, info: str) -> 'TransactionBuilder':
        self._product_info = info
        return self

    def with_gateway(self, gateway: str) -> 'TransactionBuilder':
        self._gateway = gateway
        return self

    def with_callback_url(self, url: str) -> 'TransactionBuilder':
        self._callback_url = url
        return self

    def with_user(self, user: User) -> 'TransactionBuilder':
        self._user = user
        return self
        
    def with_module(self, module: str) -> 'TransactionBuilder':
        self._module = module
        return self
    
    def with_audit_details(self, audit_details: AuditDetails) -> 'TransactionBuilder':
        self._audit_details = audit_details
        return self
    
    def with_additional_details(self, additional_details: Dict[str, Any]) -> 'TransactionBuilder':
        self._additional_details = additional_details
        return self
    
    def with_additional_fields(self, additional_fields: Dict[str, Any]) -> 'TransactionBuilder':
        self._additional_fields = additional_fields
        return self
    
    def with_response_json(self, response_json: Dict[str, Any]) -> 'TransactionBuilder':
        self._response_json = response_json
        return self
    
    def with_gateway_txn_id(self, gateway_txn_id: str) -> 'TransactionBuilder':
        self._gateway_txn_id = gateway_txn_id
        return self 
    
    def with_gateway_payment_mode(self, gateway_payment_mode: str) -> 'TransactionBuilder':
        self._gateway_payment_mode = gateway_payment_mode
        return self
    
    def with_gateway_status_code(self, gateway_status_code: str) -> 'TransactionBuilder':
        self._gateway_status_code = gateway_status_code
        return self 
    
    def with_gateway_status_msg(self, gateway_status_msg: str) -> 'TransactionBuilder':
        self._gateway_status_msg = gateway_status_msg
        return self 
    
    def with_receipt(self, receipt: str) -> 'TransactionBuilder':
        self._receipt = receipt
        return self 
    
    def with_txn_status(self, txn_status: TxnStatusEnum) -> 'TransactionBuilder':
        self._txn_status = txn_status
        return self  
    
    def with_txn_status_msg(self, txn_status_msg: str) -> 'TransactionBuilder':
        self._txn_status_msg = txn_status_msg
        return self          
    
    def with_redirect_url(self, redirect_url: str) -> 'TransactionBuilder':
        self._redirect_url = redirect_url
        return self 
    
    def with_txn_id(self, txn_id: str) -> 'TransactionBuilder':
        self._txn_id = txn_id
        return self  


    def build(self) -> Transaction:
        return Transaction(
            tenant_id=self._tenant_id,
            txn_amount=self._txn_amount,
            bill_id=self._bill_id,
            consumer_code=self._consumer_code,
            tax_and_payments=self._tax_and_payments,
            product_info=self._product_info,
            gateway=self._gateway,
            callback_url=self._callback_url,
            user=self._user,
            module=self._module,
            txn_id=self._txn_id,
            redirect_url=self._redirect_url,
            txn_status=self._txn_status,
            txn_status_msg=self._txn_status_msg,
            gateway_txn_id=self._gateway_txn_id,
            gateway_payment_mode=self._gateway_payment_mode,
            gateway_status_code=self._gateway_status_code,
            gateway_status_msg=self._gateway_status_msg,
            receipt=self._receipt,
            audit_details=self._audit_details,
            additional_details=self._additional_details,
            additional_fields=self._additional_fields,
            response_json=self._response_json,
        )

class TransactionCriteriaBuilder:
    def __init__(self):
        self._tenant_id = None
        self._txn_id = None
        self._bill_id = None
        self._user_uuid = None
        self._receipt = None
        self._consumer_code = None
        self._txn_status = None
        self._created_time = None
        self._limit = 10
        self._offset = 0

    def with_tenant_id(self, tenant_id: str) -> 'TransactionCriteriaBuilder':
        self._tenant_id = tenant_id
        return self

    def with_txn_id(self, txn_id: str) -> 'TransactionCriteriaBuilder':
        self._txn_id = txn_id
        return self

    def with_bill_id(self, bill_id: str) -> 'TransactionCriteriaBuilder':
        self._bill_id = bill_id
        return self

    def with_user_uuid(self, uuid: str) -> 'TransactionCriteriaBuilder':
        self._user_uuid = uuid
        return self
        
    def with_receipt(self, receipt: str) -> 'TransactionCriteriaBuilder':
        self._receipt = receipt
        return self
        
    def with_consumer_code(self, consumer_code: str) -> 'TransactionCriteriaBuilder':
        self._consumer_code = consumer_code
        return self
        
    def with_txn_status(self, txn_status: TxnStatusEnum) -> 'TransactionCriteriaBuilder':
        self._txn_status = txn_status
        return self
        
    def with_created_time(self, created_time: int) -> 'TransactionCriteriaBuilder':
        self._created_time = created_time
        return self
        
    def with_limit(self, limit: int) -> 'TransactionCriteriaBuilder':
        self._limit = limit
        return self
        
    def with_offset(self, offset: int) -> 'TransactionCriteriaBuilder':
        self._offset = offset
        return self

    def build(self) -> TransactionCriteria:
        return TransactionCriteria(
            tenant_id=self._tenant_id,
            txn_id=self._txn_id,
            bill_id=self._bill_id,
            user_uuid=self._user_uuid,
            receipt=self._receipt,
            consumer_code=self._consumer_code,
            created_time=self._created_time,
            txn_status=self._txn_status,
            limit=self._limit,
            offset=self._offset
        )
