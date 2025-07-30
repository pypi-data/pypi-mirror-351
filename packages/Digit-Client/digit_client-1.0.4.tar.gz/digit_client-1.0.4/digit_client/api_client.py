import requests
from .config import Config

class APIClient:
    def __init__(self):
        self.base_url = Config.API_ENDPOINT
        self.auth_token = Config.AUTH_TOKEN

    def get(self, endpoint, params=None, stream=False, require_auth=True):
        """
        Make a GET request
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            stream (bool, optional): Whether to stream the response
            require_auth (bool, optional): Whether authentication is required
            
        Returns:
            Union[dict, str]: Response JSON, text, or raw bytes if streaming
        """
        headers = {}
        if require_auth and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers, params=params, stream=stream, allow_redirects=False)
        
        if stream:
            return response.content
            
        # Handle redirects
        if response.status_code in (301, 302, 303, 307, 308):
            return response.headers.get('Location', '')
            
        # Try to parse as JSON, fallback to text
        try:
            return response.json()
        except ValueError:
            return response.text

    def post(self, endpoint, json_data=None, data=None, additional_headers=None, params=None, files=None, require_auth=True):
        """
        Make a POST request
        
        Args:
            endpoint (str): API endpoint
            json_data (dict, optional): JSON data to send
            data (dict, optional): Form data to send
            additional_headers (dict, optional): Additional headers to include
            params (dict, optional): Query parameters to include in the URL
            files (list, optional): List of tuples containing file data for upload
            require_auth (bool, optional): Whether authentication is required
            
        Returns:
            Union[dict, str]: Response JSON or text
        """
        headers = {}
        if json_data is not None:
            headers['Content-Type'] = 'application/json'
        if require_auth and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        if additional_headers:
            headers.update(additional_headers)
            
        response = requests.post(
            f"{self.base_url}/{endpoint}", 
            headers=headers,
            json=json_data if json_data is not None else None,
            data=data if data is not None else None,
            params=params if params is not None else None,
            files=files if files is not None else None
        )
        
        # Try to parse as JSON, fallback to text
        try:
            return response.json()
        except ValueError:
            return response.text

    # Add more HTTP methods as needed