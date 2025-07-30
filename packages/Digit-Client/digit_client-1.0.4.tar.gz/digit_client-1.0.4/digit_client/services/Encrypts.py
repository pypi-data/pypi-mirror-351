from ..models.Encrypts import EncReqObject, EncReqObjectBuilder, SignRequest, SignRequestBuilder, VerifyRequest, VerifyRequestBuilder, RotateKeyRequest, RotateKeyRequestBuilder,Signature
from typing import List, Optional, Any, Dict
from ..api_client import APIClient
class EncryptsService:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.api_client = api_client or APIClient()
        self.base_url = "egov-enc-service/crypto/v1"    

    def encrypt_data(self,
                   encryption_requests: List[EncReqObject]) -> Dict:
        """
        Encrypt sensitive data using government-approved cryptographic standards
        
        Args:
            encryption_requests: List of data encryption requests            
        Returns:
            Dict: Encrypted data responses
        """
        payload = {
            "encryptionRequests": [req.to_dict() for req in encryption_requests]
        }

        return self.api_client.post(
            f"{self.base_url}/_encrypt",
            json_data=payload
        )

    def decrypt_data(self,
                   decryption_request: Any) -> Dict:
        """
        Decrypt previously encrypted data
        
        Args:
            decryption_request: Decryption parameters and ciphertext (can be any object)
            
        Returns:
            Dict: Decrypted plaintext
        """
        payload = decryption_request

        return self.api_client.post(
            f"{self.base_url}/_decrypt",
            json_data=payload
        )

    def create_digital_signature(self,sign_request: SignRequest) -> Signature:
        """
        Generate digital signatures for data integrity verification
        
        Args:
            sign_request: Data and signing parameters
            
        Returns:
            Signature: Generated digital signature
        """

        payload = sign_request.to_dict()

        response = self.api_client.post(
            f"{self.base_url}/_sign",
            json_data=payload
        )
        return response

    def verify_signature(self,verify_request: VerifyRequest) -> bool:
        """
        Validate digital signatures against original data
        
        Args:
            verify_request: Signature verification parameters
            
        Returns:
            bool: True if signature is valid
        """

        payload = verify_request.to_dict()

        response = self.api_client.post(
            f"{self.base_url}/_verify",
            json_data=payload
        )
        return response

    def rotate_all_keys(self,
                        rotate_request: RotateKeyRequest) -> Dict:
        """
        Perform full key rotation for all cryptographic material
        
        Args:
            rotate_request: Key rotation parameters
            
        Returns:
            Dict: Rotation status report
        """

        payload = rotate_request.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_rotateallkeys",
            json_data=payload
        )

    def rotate_single_key(self,
                        rotate_request: RotateKeyRequest) -> Dict:
        """
        Rotate specific cryptographic key
        
        Args:
            rotate_request: Key rotation parameters
            
        Returns:
            Dict: Rotation status for specific key
        """

        payload = rotate_request.to_dict()

        return self.api_client.post(
            f"{self.base_url}/_rotatekey",
            json_data=payload
        )