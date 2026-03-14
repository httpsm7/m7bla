"""
Payment Logic Tester
Tests payment flow bypass, response tampering, and step skipping.
"""

from typing import List, Dict
from ui.animations import status_line

PAYMENT_KEYWORDS = ["payment", "pay", "checkout", "order", "purchase", "transaction"]
CONFIRMATION_KEYWORDS = ["confirm", "success", "complete", "receipt"]


class PaymentLogicTester:
    def __init__(self, request_engine):
        self.req = request_engine
        self.findings = []

    async def run(self, endpoints: List[str]) -> List[Dict]:
        payment_eps = [ep for ep in endpoints
                       if any(kw in ep.lower() for kw in PAYMENT_KEYWORDS)]
        confirm_eps = [ep for ep in endpoints
                       if any(kw in ep.lower() for kw in CONFIRMATION_KEYWORDS)]

        if not payment_eps:
            status_line("No payment endpoints found — skipping", "warn")
            return []

        for ep in payment_eps:
            status_line(f"Testing payment endpoint: {ep}", "run")
            await self._test_payment_skip(ep, confirm_eps)
            await self._test_status_tampering(ep)
            await self._test_price_manipulation(ep)

        return self.findings

    async def _test_payment_skip(self, payment_ep: str, confirm_eps: List[str]):
        """Test if confirmation endpoint can be accessed without payment."""
        for confirm_ep in confirm_eps:
            resp = await self.req.get(confirm_ep)
            if resp and resp.get("status") in [200, 201]:
                body = resp.get("text", "").lower()
                if any(word in body for word in ["success", "confirmed", "complete", "order"]):
                    self.findings.append({
                        "name": "Payment Step Skip",
                        "severity": "HIGH",
                        "endpoint": confirm_ep,
                        "description": "Confirmation endpoint accessible without completing payment",
                        "payload": f"GET {confirm_ep} (bypassing {payment_ep})",
                        "impact": "Attacker can obtain order confirmation without payment",
                    })
                    status_line(f"[VULN] Payment bypass possible via {confirm_ep}", "warn")

    async def _test_status_tampering(self, endpoint: str):
        """Test payment status parameter tampering."""
        tamper_payloads = [
            {"status": "success", "payment_status": "paid"},
            {"txn_status": "SUCCESS", "paid": True},
            {"payment_result": "APPROVED"},
        ]
        for payload in tamper_payloads:
            resp = await self.req.post(endpoint, payload)
            if resp and resp.get("status") in [200, 201]:
                body = resp.get("text", "").lower()
                if any(word in body for word in ["success", "confirmed", "order"]):
                    self.findings.append({
                        "name": "Payment Status Tampering",
                        "severity": "HIGH",
                        "endpoint": endpoint,
                        "description": "Server accepted forged payment status parameter",
                        "payload": str(payload),
                        "impact": "Attacker can forge payment confirmation",
                    })

    async def _test_price_manipulation(self, endpoint: str):
        """Test price field manipulation."""
        resp = await self.req.post(endpoint, {"price": 1, "amount": 1, "total": 1})
        if resp and resp.get("status") in [200, 201]:
            self.findings.append({
                "name": "Payment Price Manipulation",
                "severity": "HIGH",
                "endpoint": endpoint,
                "description": "Payment accepted with manipulated price=1",
                "payload": "price=1&amount=1&total=1",
                "impact": "Attacker can complete payment at manipulated price",
            })
