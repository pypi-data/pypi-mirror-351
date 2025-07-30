from typing import Dict, List, Optional, Any
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.Transactions import (
    Transaction, TransactionCriteria,
    TxnStatusEnum, TaxAndPayment
)

class TransactionService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "transaction/v1"
        self.gateway_url = "gateway/v1"

    def create_transaction(self,
                         transaction: Transaction,
                         request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Create a new financial transaction with tax calculations
        
        Args:
            transaction: Transaction details including tax components
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Created transaction record with system-generated ID
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "Transaction": transaction.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_create",
            json_data=payload
        )

    def search_transactions(self,
                          criteria: TransactionCriteria,
                          request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Search transactions based on customizable filters
        
        Args:
            criteria: Search parameters (date ranges, amounts, statuses)
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Paginated list of matching transactions
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict()
        }

        # Convert criteria to query parameters
        query_params = criteria.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_search",
            json_data=payload,
            params=query_params
        )

    def update_transaction(self,
                         update_params: Dict[str, str],
                         request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Update transaction status or metadata
        
        Args:
            update_params: Map of fields to update
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Updated transaction record
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict()
        }

        return self.api_client.post(
            f"{self.base_url}/_update",
            json_data=payload,
            params=update_params
        )

    def search_gateway_transactions(self) -> Dict:
        """
        Search payment gateway transactions
        
        Returns:
            Dict: Payment gateway transaction records
        """

        return self.api_client.post(
            f"{self.gateway_url}/_search",
        )
