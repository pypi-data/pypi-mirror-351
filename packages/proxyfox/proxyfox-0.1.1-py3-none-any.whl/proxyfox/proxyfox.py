import requests
from typing import List, Dict, Optional

class ProxyFetcher:
    def __init__(self):
        """Initialize ProxyFetcher"""
        self.api_url = "https://papi.proxiware.com/proxies"
        self.headers = {
            "accept": "*/*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "accept-language": "en-US,en;q=0.8"
        }
        # Map common country codes to their ISO codes
        self.country_map = {
            'UK': 'GB'  # Map UK to GB (Great Britain)
        }

    def _get_country_code(self, country: str) -> str:
        """Convert country code to proper ISO format"""
        return self.country_map.get(country.upper(), country.upper())

    def get_proxies(self, max_speed_ms: Optional[int] = None, 
                   country: Optional[str] = None,
                   protocol: Optional[str] = None) -> List[str]:
        """
        Get list of proxies in ip:port format
        
        Args:
            max_speed_ms: Optional speed filter in milliseconds
            country: Country code (e.g., 'US', 'GB', 'UK')
            protocol: Optional protocol filter ('http' or 'https')
        
        Returns:
            List of proxy strings in ip:port format
        """
        params = {}
        if country:
            params['country'] = self._get_country_code(country)
        if protocol:
            params['protocol'] = protocol.lower()

        try:
            response = requests.get(self.api_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            proxies = []
            for proxy in data["proxies"]:
                if max_speed_ms and proxy["speed_ms"] > max_speed_ms:
                    continue
                proxies.append(f"{proxy['addr']}:{proxy['port']}")
                
            return proxies
        except Exception as e:
            print(f"Error fetching proxies: {e}")
            return []

    def get_fast_proxies(self, limit: int = 5, protocol: Optional[str] = None) -> List[str]:
        """
        Get fastest proxies
        
        Args:
            limit: Number of proxies to return (default 5)
            protocol: Optional protocol filter ('http' or 'https')
            
        Returns:
            List of fastest proxy strings in ip:port format
        """
        return self.get_proxies(max_speed_ms=1000, protocol=protocol)[:limit]

    def get_http_proxies(self, max_speed_ms: Optional[int] = None) -> List[str]:
        """
        Get HTTP proxies
        
        Args:
            max_speed_ms: Optional speed filter in milliseconds
            
        Returns:
            List of HTTP proxy strings in ip:port format
        """
        return self.get_proxies(max_speed_ms=max_speed_ms, protocol='http')

    def get_https_proxies(self, max_speed_ms: Optional[int] = None) -> List[str]:
        """
        Get HTTPS proxies
        
        Args:
            max_speed_ms: Optional speed filter in milliseconds
            
        Returns:
            List of HTTPS proxy strings in ip:port format
        """
        return self.get_proxies(max_speed_ms=max_speed_ms, protocol='https')

    def get_country_proxies(self, country_code: str, 
                          max_speed_ms: Optional[int] = None,
                          protocol: Optional[str] = None) -> List[str]:
        """
        Get proxies from specific country
        
        Args:
            country_code: Country code (e.g., 'US', 'GB', 'UK')
                        Note: For UK proxies, both 'GB' and 'UK' are accepted
            max_speed_ms: Optional speed filter in milliseconds
            protocol: Optional protocol filter ('http' or 'https')
            
        Returns:
            List of proxy strings in ip:port format from specified country
        """
        return self.get_proxies(max_speed_ms=max_speed_ms, 
                              country=country_code,
                              protocol=protocol)

    def get_all_proxies(self) -> List[str]:
        """
        Get all available proxies
        
        Returns:
            List of all proxy strings in ip:port format
        """
        return self.get_proxies()
