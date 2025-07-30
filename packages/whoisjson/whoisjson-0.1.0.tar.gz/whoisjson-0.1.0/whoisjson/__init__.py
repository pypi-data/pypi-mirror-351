"""
A Python client for the whois-json API service.
"""

import requests
from typing import Dict, Any, Optional

class WhoisJsonClient:
    """A client for interacting with the whois-json API service."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the WhoisJson client.
        
        Args:
            api_key (str, optional): Your API key for the service. Required for premium features.
        """
        self.api_key = api_key
        self.base_url = "https://whoisjson.com/api/v1"
        
    def _make_request(self, endpoint: str, domain: str) -> Dict[str, Any]:
        """
        Make a request to the API.
        
        Args:
            endpoint (str): The API endpoint to call.
            domain (str): The domain name to query.
            
        Returns:
            dict: The API response.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the domain is invalid.
        """
        if not domain:
            raise ValueError("Domain name is required")
            
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        response = requests.get(
            f"{self.base_url}/{endpoint}/{domain}",
            headers=headers
        )
        response.raise_for_status()
        
        return response.json()
        
    def whois(self, domain: str) -> Dict[str, Any]:
        """
        Perform a WHOIS lookup for a domain.
        
        Args:
            domain (str): The domain name to look up.
            
        Returns:
            dict: The WHOIS information for the domain.
        """
        return self._make_request("whois", domain)
        
    def nslookup(self, domain: str) -> Dict[str, Any]:
        """
        Perform a DNS lookup for a domain.
        
        Args:
            domain (str): The domain name to look up.
            
        Returns:
            dict: The DNS records for the domain.
        """
        return self._make_request("nslookup", domain)
        
    def ssl_cert_check(self, domain: str) -> Dict[str, Any]:
        """
        Check SSL certificate information for a domain.
        
        Args:
            domain (str): The domain name to check SSL certificate for.
            
        Returns:
            dict: The SSL certificate information for the domain.
        """
        return self._make_request("ssl-cert-check", domain)
        
    # Alias for backward compatibility
    lookup = whois 