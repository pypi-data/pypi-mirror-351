import os
import requests
import websocket
import json
import threading
from typing import Dict, Any, Optional, List

class PoridihCloud:
    """
    Main client for interacting with Poridhi Cloud infrastructure.
    
    Attributes:
        api_key (Optional[str]): API key for authentication
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None, 
        api_key: Optional[str] = None
    ):
        """
        Initialize the Poridhi Cloud client.
        
        Args:
            api_key (str, optional): API key for authentication. 
                Defaults to environment variable PORIDHI_CLOUD_API_KEY.
        """
        self.base_url = "https://api-bcp.poridhi.cloud"
        self.api_key = api_key or os.getenv('PORIDHI_CLOUD_API_KEY')
        self._session = requests.Session()
        
        if self.api_key:
            self._session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Poridhi Cloud API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            data (dict, optional): Request payload
            params (dict, optional): Query parameters
        
        Returns:
            dict: Response data
        
        Raises:
            PoridihCloudError: For API-related errors
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self._session.request(
                method, 
                url, 
                json=data, 
                params=params
            )
            
            response.raise_for_status()
            return response.json() if response.content else {}
        
        except requests.RequestException as e:
            raise PoridihCloudError(f"API Request Error: {str(e)}")
    def create_user(
        self,

    ) -> Dict[str, Any]:
        """
        Create New user 

        Returns:
            dict: user create
        
        """
        return self._make_request('POST','/create-user')
    def get_machineId(
        self, 
        
    ) -> Dict[str, Any]:
        """
        Launch a new machine with specified resources.
        
       
        
        Returns:
            dict: Machine details
        """
        # payload = {
        #     "cpu": cpu,
        #     "memory": memory,
        #     "gpu": gpu or "",
        #     "gpuCount": gpu_count
        # }
        
        return self._make_request('GET', '/get-machine')
    
    def codeserver(
        self, 
        cpu: int, 
        memory: int, 
        gpu: Optional[str] = None, 
        port: Optional[int] = None,
        serviceType: Optional[str]= None,
        duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Allocate a worker with specified resources.
        
        Args:
            cpu (int): Number of CPU cores
            memory (int): Memory in MB
            gpu (str, optional): GPU type
            gpu_count (int, optional): Number of GPUs
            image (str, optional): Custom container image
            port (int, optional): Custom container port
            serviceType (str,optional): service type
            machineId (str, optional): Specific machine to allocate on
            duration (int, optional): duration
        
        Returns:
            dict: Allocated worker details
        """
        payload = {
            "cpu": cpu,
            "memory": memory,
            "gpu": gpu or "",
            "port": port,
            "serviceType":serviceType,
            "duration" : duration
        }
        
        return self._make_request('POST', '/allocate-bcp', data=payload)
    
    def podStatus(
            self,
            deploymentname: str,

    ) -> Dict[str, Any]:
        """
          Check pod status 

          Args: 
              deploymentname (str): name of the deployment 

          Returns: 
              dict: Pod status
        """
        
        return self._make_request('GET', "/check-vscode-status", params={'deploymentname':deploymentname})
    
    # def list_machines(self) -> List[Dict[str, Any]]:
    #     """
    #     List all available machines.
        
    #     Returns:
    #         list: Machine details
    #     """
    #     return self._make_request('GET', '/machines')
    
    # def list_machine_resources(self) -> List[Dict[str, Any]]:
    #     """
    #     List machine resources.
        
    #     Returns:
    #         list: Machine resource details
    #     """
    #     return self._make_request('GET', '/machine-resources')
    
    # def get_service_status(self, worker_id: str) -> Dict[str, Any]:
    #     """
    #     Get status of a specific worker service.
        
    #     Args:
    #         worker_id (str): ID of the worker
        
    #     Returns:
    #         dict: Service status details
    #     """
    #     return self._make_request('GET', '/service/status', params={'worker_id': worker_id})
    
    # def stream_generate(self, worker_id: str, model: str = 'deepseek-coder', prompt: str = '', **kwargs):
    #     """
    #     Stream text generation from a worker.
        
    #     Args:
    #         worker_id (str): Worker ID to use for generation
    #         model (str, optional): Model name
    #         prompt (str, optional): Input prompt
    #         **kwargs: Additional generation parameters
        
    #     Yields:
    #         str: Generated tokens
    #     """
    #     params = {
    #         'model': model,
    #         'prompt': prompt,
    #         **kwargs
    #     }
        
    #     # Use self._session instead of direct requests to include authorization headers
    #     with self._session.post(
    #         f"{self.base_url}/stream", 
    #         params={'workerId': worker_id},
    #         json=params, 
    #         stream=True
    #     ) as response:
    #         response.raise_for_status()  # Added error handling
    #         for line in response.iter_lines():
    #             if line:
    #                 yield line.decode('utf-8')
    
    

class PoridihCloudError(Exception):
    """Base exception for Poridhi Cloud SDK."""
    pass