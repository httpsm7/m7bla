"""
IDOR Engine
Tests insecure direct object references on discovered endpoints.
"""

import re
from typing import List, Dict
from ui.animations import status_line

IDOR_PARAMS = ["user_id", "uid", "id", "account_id", "profile_id", "order_id", "sid"]
BASE_IDS = [1, 2, 3, 100, 101, 1000, 9999]


class IDOREngine:
    def __init__(self, request_engine):
        self.req = request_engine
        self.findings = []

    async def run(self, endpoints: List[str]) -> List[Dict]:
        idor_candidates = self._find_idor_candidates(endpoints)

        if not idor_candidates:
            status_line("No IDOR candidates found", "warn")
            return []

        for ep in idor_candidates:
            status_line(f"Testing IDOR: {ep}", "run")
            await self._test_id_enumeration(ep)
            await self._test_path_traversal_id(ep)

        return self.findings

    def _find_idor_candidates(self, endpoints: List[str]) -> List[str]:
        """Find endpoints with ID-like patterns."""
        candidates = []
        for ep in endpoints:
            if re.search(r'/\d+', ep) or any(p in ep.lower() for p in IDOR_PARAMS):
                candidates.append(ep)
            elif any(p in ep.lower() for p in ["profile", "account", "user", "order"]):
                candidates.append(ep)
        return candidates

    async def _test_id_enumeration(self, endpoint: str):
        """Test sequential ID enumeration."""
        for test_id in BASE_IDS:
            # Replace any existing ID in path
            test_url = re.sub(r'/\d+', f'/{test_id}', endpoint)
            if test_url == endpoint:
                test_url = endpoint.rstrip('/') + f'/{test_id}'

            resp = await self.req.get(test_url)
            if resp and resp.get("status") == 200:
                body = resp.get("text", "")
                if len(body) > 50:  # Non-empty meaningful response
                    self.findings.append({
                        "name": "Potential IDOR - ID Enumeration",
                        "severity": "HIGH",
                        "endpoint": test_url,
                        "description": f"Endpoint returned data for ID={test_id} without authorization check",
                        "payload": f"GET {test_url}",
                        "impact": "Access other users' data by changing ID parameter",
                    })
                    status_line(f"[VULN] IDOR candidate: {test_url}", "warn")
                    break  # Report once per endpoint

    async def _test_path_traversal_id(self, endpoint: str):
        """Test for missing authorization on object access."""
        for param in IDOR_PARAMS:
            if param in endpoint.lower():
                test_url = re.sub(
                    rf'([?&]{param}=)\d+', rf'\g<1>99999', endpoint
                )
                resp = await self.req.get(test_url)
                if resp and resp.get("status") == 200:
                    self.findings.append({
                        "name": "IDOR via Query Parameter",
                        "severity": "HIGH",
                        "endpoint": test_url,
                        "description": f"Accessed object by modifying {param} parameter",
                        "payload": f"{param}=99999",
                        "impact": "Unauthorized access to other users' resources",
                    })
