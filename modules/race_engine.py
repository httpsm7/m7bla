"""
Race Condition Engine
Tests parallel request race conditions on critical endpoints.
"""

import asyncio
from typing import List, Dict
from ui.animations import status_line, race_animation

RACE_KEYWORDS = ["recharge", "topup", "wallet", "payment", "coupon", "redeem", "apply"]
RACE_COUNT = 20


class RaceEngine:
    def __init__(self, request_engine):
        self.req = request_engine
        self.findings = []

    async def run(self, endpoints: List[str]) -> List[Dict]:
        race_candidates = [ep for ep in endpoints
                           if any(kw in ep.lower() for kw in RACE_KEYWORDS)]

        if not race_candidates:
            status_line("No race condition candidates found", "warn")
            return []

        for ep in race_candidates:
            status_line(f"Race condition test: {ep}", "run")
            await self._test_race(ep)

        return self.findings

    async def _test_race(self, endpoint: str):
        """Send concurrent requests to detect race conditions."""
        race_animation(endpoint, count=min(RACE_COUNT, 10))

        payload = {"amount": 100, "action": "recharge"}
        results = await self.req.concurrent_requests(endpoint, "POST", payload, count=RACE_COUNT)

        success_count = sum(1 for r in results if r.get("status") in [200, 201])
        unique_responses = len(set(r.get("text", "")[:100] for r in results))

        status_line(f"Sent {RACE_COUNT} concurrent requests — {success_count} succeeded", "info")

        if success_count > 1:
            self.findings.append({
                "name": "Race Condition - Parallel Request Abuse",
                "severity": "HIGH",
                "endpoint": endpoint,
                "description": f"{success_count}/{RACE_COUNT} concurrent requests succeeded — potential double-processing",
                "payload": f"50x concurrent POST {endpoint}",
                "impact": "Balance duplication, coupon reuse, or free credits via race window",
            })
            status_line(f"[VULN] Race condition potential at {endpoint}", "warn")
