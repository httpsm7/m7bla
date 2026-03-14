"""
Request Engine
Handles all HTTP requests with proxy, session, and mutation support.
Supports httpx (preferred) with fallback to urllib.
"""

import asyncio
import json
from typing import Optional, Dict, List, Any
from ui.animations import status_line

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

import urllib.request
import urllib.parse


class RequestEngine:
    def __init__(self, base_url: str, proxy: Optional[str] = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.proxy = proxy
        self.timeout = timeout
        self.session_cookies = {}
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) m7bla/1.0 Milkyway-Intelligence",
            "Accept": "application/json, text/html, */*",
            "Content-Type": "application/json",
        }
        self._discovered_params: Dict[str, List[str]] = {}

    async def probe(self, url: str) -> Optional[Dict]:
        """Probe a URL and return status/metadata."""
        try:
            return await self.get(url)
        except Exception:
            return None

    def _make_client(self):
        """Create an httpx AsyncClient with optional proxy (compatible with httpx 0.20+)."""
        kwargs = {"timeout": self.timeout, "follow_redirects": True}
        if self.proxy:
            # httpx >= 0.23 uses 'proxy', older uses 'proxies'
            try:
                return httpx.AsyncClient(proxy=self.proxy, **kwargs)
            except TypeError:
                return httpx.AsyncClient(proxies=self.proxy, **kwargs)
        return httpx.AsyncClient(**kwargs)

    async def get(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Async GET request."""
        h = {**self.default_headers, **(headers or {})}
        try:
            if HTTPX_AVAILABLE:
                async with self._make_client() as client:
                    r = await client.get(url, headers=h)
                    return {
                        "status": r.status_code,
                        "text": r.text,
                        "headers": dict(r.headers),
                        "url": str(r.url),
                    }
            else:
                return self._urllib_get(url, h)
        except Exception as e:
            return {"status": None, "error": str(e), "text": ""}

    def _urllib_get(self, url: str, headers: Dict) -> Dict:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return {
                    "status": resp.status,
                    "text": resp.read().decode("utf-8", errors="ignore"),
                    "headers": dict(resp.headers),
                    "url": url,
                }
        except Exception as e:
            return {"status": None, "error": str(e), "text": ""}

    async def post(self, url: str, data: Any, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Async POST request."""
        h = {**self.default_headers, **(headers or {})}
        body = json.dumps(data) if isinstance(data, dict) else str(data)
        try:
            if HTTPX_AVAILABLE:
                async with self._make_client() as client:
                    r = await client.post(url, content=body, headers=h)
                    return {
                        "status": r.status_code,
                        "text": r.text,
                        "headers": dict(r.headers),
                        "url": str(r.url),
                    }
            else:
                return self._urllib_post(url, body, h)
        except Exception as e:
            return {"status": None, "error": str(e), "text": ""}

    def _urllib_post(self, url: str, body: str, headers: Dict) -> Dict:
        try:
            data = body.encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return {
                    "status": resp.status,
                    "text": resp.read().decode("utf-8", errors="ignore"),
                    "headers": dict(resp.headers),
                    "url": url,
                }
        except Exception as e:
            return {"status": None, "error": str(e), "text": ""}

    async def concurrent_requests(self, url: str, method: str, data: Any,
                                   count: int = 50) -> List[Dict]:
        """Send concurrent requests for race condition testing."""
        tasks = []
        for _ in range(count):
            if method.upper() == "POST":
                tasks.append(self.post(url, data))
            else:
                tasks.append(self.get(url))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, dict)]

    async def discover_parameters(self, endpoints: List[str]) -> Dict[str, List[str]]:
        """Discover query/body parameters from endpoint responses."""
        import re
        all_params = {}
        for ep in endpoints:
            resp = await self.get(ep)
            if resp and resp.get("text"):
                params = re.findall(r'name=["\']([^"\']+)["\']', resp["text"])
                params += re.findall(r'"([a-z_]+)":\s*(?:\d+|")', resp["text"])
                if params:
                    all_params[ep] = list(set(params))
        self._discovered_params = all_params
        return all_params
