"""
Burp Suite Proxy Integration
Routes m7bla traffic through Burp Suite for manual interception.
"""

from typing import Optional


class BurpProxy:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.proxy_url = f"http://{host}:{port}"

    def get_proxy_dict(self) -> dict:
        """Returns proxy dict compatible with httpx/requests."""
        return {
            "http://": self.proxy_url,
            "https://": self.proxy_url,
        }

    def __str__(self) -> str:
        return self.proxy_url
