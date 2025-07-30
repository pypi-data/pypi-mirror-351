import requests
import time
import threading
from typing import List, Dict, Optional, Union
from queue import Queue

class ProxyPool:
    def __init__(self, size: int = 10, refresh_interval: int = 300, **filters):
        """
        Initialize an auto-updating proxy pool
        
        Args:
            size: Number of proxies to maintain in pool
            refresh_interval: Time in seconds between updates (default 5 minutes)
            **filters: Any proxy filters (protocol, country, etc.)
        """
        self.size = size
        self.refresh_interval = refresh_interval
        self.filters = filters
        self.proxies = Queue()
        self.fetcher = ProxyFetcher()
        self._stop = False
        self._update_thread = threading.Thread(target=self._auto_update)
        self._update_thread.daemon = True
        self._update_thread.start()
    
    def _auto_update(self):
        """Background thread to update proxies"""
        while not self._stop:
            proxies = self.fetcher.get_proxies(**self.filters)[:self.size]
            # Clear current queue
            while not self.proxies.empty():
                self.proxies.get()
            # Add new proxies
            for proxy in proxies:
                self.proxies.put(proxy)
            time.sleep(self.refresh_interval)
    
    def get(self) -> str:
        """Get a proxy from the pool"""
        if self.proxies.empty():
            return self.fetcher.get_single_proxy(**self.filters)
        return self.proxies.get()
    
    def all(self) -> List[str]:
        """Get all current proxies in the pool"""
        return list(self.proxies.queue)
    
    def __del__(self):
        """Cleanup on deletion"""
        self._stop = True
        if self._update_thread.is_alive():
            self._update_thread.join()

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
        
    def get_single_proxy(self, protocol: Optional[str] = None,
                        country: Optional[str] = None,
                        max_speed_ms: Optional[int] = None) -> str:
        """
        Get a single working proxy
        
        Args:
            protocol: Optional protocol filter ('http' or 'https')
            country: Country code (e.g., 'US', 'GB')
            max_speed_ms: Optional speed filter in milliseconds
            
        Returns:
            Single proxy string in ip:port format
        """
        proxies = self.get_proxies(protocol=protocol,
                                 country=country,
                                 max_speed_ms=max_speed_ms)
        return proxies[0] if proxies else ""
        
    def get_proxy_count(self, count: int,
                       protocol: Optional[str] = None,
                       country: Optional[str] = None,
                       max_speed_ms: Optional[int] = None) -> List[str]:
        """
        Get specified number of proxies
        
        Args:
            count: Number of proxies to return
            protocol: Optional protocol filter ('http' or 'https')
            country: Country code (e.g., 'US', 'GB')
            max_speed_ms: Optional speed filter in milliseconds
            
        Returns:
            List of proxy strings in ip:port format
        """
        proxies = self.get_proxies(protocol=protocol,
                                 country=country,
                                 max_speed_ms=max_speed_ms)
        return proxies[:count]

# Simplified interface
def get_one(**filters) -> str:
    """Get a single proxy with optional filters"""
    fetcher = ProxyFetcher()
    return fetcher.get_single_proxy(**filters)

def get(count: int, **filters) -> List[str]:
    """Get specified number of proxies with optional filters"""
    fetcher = ProxyFetcher()
    return fetcher.get_proxy_count(count, **filters)

def create_pool(size: int = 10, refresh_interval: int = 300, **filters) -> ProxyPool:
    """Create an auto-updating proxy pool"""
    return ProxyPool(size=size, refresh_interval=refresh_interval, **filters)
