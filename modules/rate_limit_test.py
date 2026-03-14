"""
Rate Limit Tester
Tests for missing or bypassable rate limiting.
"""

import asyncio
from typing import List, Dict
from ui.animations import status_line

RATE_LIMIT_TARGETS = ["login", "signin", "auth", "otp", "verify", "reset", "forgot"]
BYPASS_HEADERS = [
    {"X-Forwarded-For": "1.2.3.4"},
    {"X-Real-IP": "10.0.0.1"},
    {"X-Originating-IP": "192.168.1.1"},
    {"CF-Connecting-IP": "172.16.0.1"},
]


class RateLimitTester:
    def __init__(self, request_engine):
        self.req = request_engine
        self.findings = []

    async def run(self, endpoints: List[str]) -> List[Dict]:
        target_eps = [ep for ep in endpoints
                      if any(kw in ep.lower() for kw in RATE_LIMIT_TARGETS)]

        if not target_eps:
            status_line("No rate-limit-sensitive endpoints found", "warn")
            return []

        for ep in target_eps:
            status_line(f"Rate limit test: {ep}", "run")
            await self._test_no_rate_limit(ep)
            await self._test_ip_header_bypass(ep)

        return self.findings

    async def _test_no_rate_limit(self, endpoint: str):
        """Send 30 rapid requests and check if blocked."""
        tasks = [
            self.req.post(endpoint, {"username": f"test{i}@test.com", "password": "test123"})
            for i in range(30)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = [r for r in results if isinstance(r, dict) and r.get("status") not in [429, 403, None]]

        if len(success) > 20:
            self.findings.append({
                "name": "Missing Rate Limiting",
                "severity": "MEDIUM",
                "endpoint": endpoint,
                "description": f"{len(success)}/30 rapid requests succeeded without rate limiting",
                "payload": "30x rapid POST requests",
                "impact": "Brute force attacks possible — no lockout or throttling",
            })
            status_line(f"[VULN] No rate limit at {endpoint}", "warn")

    async def _test_ip_header_bypass(self, endpoint: str):
        """Test if IP-based rate limiting can be bypassed via headers."""
        for headers in BYPASS_HEADERS:
            tasks = [
                self.req.post(endpoint, {"username": "test@test.com", "password": "x"}, headers=headers)
                for _ in range(10)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success = [r for r in results if isinstance(r, dict) and r.get("status") == 200]

            if len(success) >= 9:
                header_name = list(headers.keys())[0]
                self.findings.append({
                    "name": "Rate Limit IP Header Bypass",
                    "severity": "MEDIUM",
                    "endpoint": endpoint,
                    "description": f"Rate limiting bypassed using {header_name} header",
                    "payload": f"{header_name}: <spoofed-ip>",
                    "impact": "Attacker can bypass IP-based brute force protection",
                })
                break
