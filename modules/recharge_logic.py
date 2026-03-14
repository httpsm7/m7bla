"""
Recharge Logic Tester
Tests amount tampering, negative values, replay attacks on recharge endpoints.
"""

import asyncio
from typing import List, Dict
from ui.animations import status_line, typing_effect

RECHARGE_KEYWORDS = ["recharge", "topup", "top-up", "wallet/credit", "balance/add"]
MUTATION_VALUES = [0, -1, -100, 0.001, 999999999, "null", "undefined", True, False, ""]


class RechargeLogicTester:
    def __init__(self, request_engine):
        self.req = request_engine
        self.findings = []

    async def run(self, endpoints: List[str]) -> List[Dict]:
        recharge_eps = [ep for ep in endpoints
                        if any(kw in ep.lower() for kw in RECHARGE_KEYWORDS)]

        if not recharge_eps:
            status_line("No recharge endpoints found — skipping", "warn")
            return []

        for ep in recharge_eps:
            status_line(f"Testing recharge endpoint: {ep}", "run")
            await self._test_amount_tampering(ep)
            await self._test_negative_values(ep)
            await self._test_zero_amount(ep)

        return self.findings

    async def _test_amount_tampering(self, endpoint: str):
        """Test if amount can be tampered to small values."""
        payloads = [
            {"amount": 1, "original": 100},
            {"amount": 0.01, "original": 100},
        ]
        for payload in payloads:
            resp = await self.req.post(endpoint, {"amount": payload["amount"]})
            if resp and resp.get("status") in [200, 201]:
                self.findings.append({
                    "name": "Recharge Amount Tampering",
                    "severity": "HIGH",
                    "endpoint": endpoint,
                    "description": f"Server accepted modified amount={payload['amount']} instead of {payload['original']}",
                    "payload": f"amount={payload['amount']}",
                    "impact": "Attacker can recharge full value by paying minimal amount",
                })
                status_line(f"[VULN] Amount tampering accepted at {endpoint}", "warn")

    async def _test_negative_values(self, endpoint: str):
        """Test if negative amount values are accepted."""
        resp = await self.req.post(endpoint, {"amount": -100})
        if resp and resp.get("status") in [200, 201]:
            self.findings.append({
                "name": "Negative Recharge Amount",
                "severity": "HIGH",
                "endpoint": endpoint,
                "description": "Server accepted negative amount value",
                "payload": "amount=-100",
                "impact": "May cause balance overflow or deduct from other users",
            })
            status_line(f"[VULN] Negative amount accepted at {endpoint}", "warn")

    async def _test_zero_amount(self, endpoint: str):
        """Test if zero amount is accepted."""
        resp = await self.req.post(endpoint, {"amount": 0})
        if resp and resp.get("status") in [200, 201]:
            self.findings.append({
                "name": "Zero Amount Recharge",
                "severity": "MEDIUM",
                "endpoint": endpoint,
                "description": "Server accepted zero amount recharge",
                "payload": "amount=0",
                "impact": "Free recharge trigger without payment",
            })
