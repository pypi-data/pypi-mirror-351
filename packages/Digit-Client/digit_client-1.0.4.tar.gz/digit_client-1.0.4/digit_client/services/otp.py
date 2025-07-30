from typing import Dict, Optional
from ..api_client import APIClient
from ..request_config import RequestConfig, RequestInfo
from ..models.Otp import Otp, UserOtp

class EgovOtpService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.user_otp_base = "user-otp/v1"
        self.otp_base = "otp/v1"

    
    def validate_otp(self,
                   otp: Otp,
                   request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Validate user-provided OTP  
        
        Args:
            user_otp: OTP validation parameters
            request_info: Authentication and request metadata
            
        Returns:
            Dict: Validation result with success status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "otp": otp.to_dict()
        }

        return self.api_client.post(
            f"{self.otp_base}/_validate",
            json_data=payload
        )

    def create_otp(self,
                 otp: Otp,
                 request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Generate and send OTP for authentication
        
        Args:
            otp_request: OTP generation parameters
            request_info: Authentication and request metadata
            
        Returns:
            Dict: OTP generation status with UUID
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "otp": otp.to_dict()
        }

        return self.api_client.post(
            f"{self.otp_base}/_create",
            json_data=payload
        )

    def search_otp(self,
                 search_request: Otp,
                 request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Verify OTP status and validity
        
        Args:
            search_request: OTP verification parameters
            request_info: Authentication and request metadata
            
        Returns:
            Dict: OTP validation status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "otp": search_request.to_dict()
        }

        return self.api_client.post(
            f"{self.otp_base}/_search",
            json_data=payload
        )
        
class UserOtpService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.user_otp_base = "user-otp/v1"
    
    def user_send_otp(self,
                user_otp: UserOtp,
                request_info: Optional[RequestInfo] = None) -> Dict:
        """
        Send OTP to mobile number for authentication
        
        Args:
            otp: OTP request parameters
            request_info: Authentication and request metadata
            
        Returns:
            Dict: OTP transmission status
        """
        request_info = request_info or RequestConfig.get_request_info()
        
        payload = {
            "RequestInfo": request_info.to_dict(),
            "otp": user_otp.to_dict()
        }

        return self.api_client.post(
            f"{self.user_otp_base}/_send",
            json_data=payload
        )
