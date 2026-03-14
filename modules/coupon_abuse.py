"""
Coupon Abuse Tester
Tests coupon/promo code reuse, stacking, and bypass.
"""

from typing import List, Dict
from ui.animations import status_line

COUPON_KEYWORDS = ["coupon", "promo", "discount", "voucher", "code", "redeem"]
TEST_CODES = ["TEST10", "SAVE50", "PROMO100", "DISC20", "FREE", "100OFF", "ADMIN", "DEBUG"]


class CouponAbuseTester:
    def __init__(self, request_engine):
        self.req = request_engine
        self.findings = []

    async def run(self, endpoints: List[str]) -> List[Dict]:
        coupon_eps = [ep for ep in endpoints
                      if any(kw in ep.lower() for kw in COUPON_KEYWORDS)]

        if not coupon_eps:
            status_line("No coupon endpoints found — skipping", "warn")
            return []

        for ep in coupon_eps:
            status_line(f"Testing coupon abuse: {ep}", "run")
            await self._test_code_enumeration(ep)
            await self._test_negative_discount(ep)

        return self.findings

    async def _test_code_enumeration(self, endpoint: str):
        """Test common/guessable coupon codes."""
        for code in TEST_CODES:
            resp = await self.req.post(endpoint, {"coupon_code": code, "code": code})
            if resp and resp.get("status") == 200:
                body = resp.get("text", "").lower()
                if any(w in body for w in ["discount", "applied", "valid", "success"]):
                    self.findings.append({
                        "name": "Guessable Coupon Code",
                        "severity": "MEDIUM",
                        "endpoint": endpoint,
                        "description": f"Common coupon code '{code}' accepted",
                        "payload": f"coupon_code={code}",
                        "impact": "Unauthorized discount via predictable coupon codes",
                    })
                    status_line(f"[VULN] Coupon code '{code}' accepted at {endpoint}", "warn")

    async def _test_negative_discount(self, endpoint: str):
        """Test negative discount value injection."""
        resp = await self.req.post(endpoint, {"discount": -100, "amount": -100})
        if resp and resp.get("status") == 200:
            self.findings.append({
                "name": "Negative Discount Injection",
                "severity": "HIGH",
                "endpoint": endpoint,
                "description": "Negative discount value accepted — may increase balance",
                "payload": "discount=-100",
                "impact": "Attacker gains credits instead of discount",
            })
