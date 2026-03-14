"""
Workflow Mapper Engine
Crawls and maps application workflow graph.
Gracefully falls back if 'rich' is not installed.
"""

import re
import asyncio
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Dict
from ui.animations import status_line

try:
    from rich.console import Console
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False

WORKFLOW_KEYWORDS = {
    "auth":         ["login", "signin", "register", "signup", "logout", "auth", "oauth"],
    "search":       ["search", "find", "lookup", "query"],
    "payment":      ["payment", "pay", "checkout", "order", "purchase", "buy"],
    "recharge":     ["recharge", "topup", "top-up", "wallet", "credit", "balance"],
    "confirmation": ["confirm", "success", "complete", "receipt", "invoice"],
    "account":      ["profile", "account", "user", "settings", "dashboard"],
    "api":          ["api", "v1", "v2", "graphql", "rest", "endpoint"],
}

COMMON_PATHS = [
    "/", "/login", "/signup", "/register", "/logout",
    "/dashboard", "/profile", "/account", "/settings",
    "/api/user", "/api/auth", "/api/login",
    "/api/recharge", "/api/topup", "/api/wallet",
    "/api/payment", "/api/checkout", "/api/order",
    "/api/search", "/api/balance",
    "/payment", "/checkout", "/cart", "/order",
    "/recharge", "/topup", "/wallet",
    "/search", "/results",
]


class WorkflowMapper:
    def __init__(self, request_engine):
        self.request_engine = request_engine
        self.visited = set()

    async def map(self, target: str) -> Tuple[List[Dict], List[str]]:
        status_line("Probing common paths...", "info")
        endpoints = await self._probe_common_paths(target)

        status_line("Crawling discovered pages...", "info")
        deep_endpoints = await self._crawl(target, endpoints)
        all_endpoints = list(set(endpoints + deep_endpoints))

        status_line("Classifying workflow stages...", "info")
        workflows = self._classify_workflows(all_endpoints)

        return workflows, all_endpoints

    async def _probe_common_paths(self, target: str) -> List[str]:
        found = []
        tasks = [self.request_engine.probe(urljoin(target, path)) for path in COMMON_PATHS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for path, result in zip(COMMON_PATHS, results):
            if isinstance(result, dict) and result.get("status") not in [404, None]:
                found.append(urljoin(target, path))
                status_line(f"[{result.get('status', '?')}] {path}", "success")

        return found

    async def _crawl(self, target: str, seed_endpoints: List[str]) -> List[str]:
        discovered = []
        for url in seed_endpoints[:10]:
            if url in self.visited:
                continue
            self.visited.add(url)
            try:
                resp = await self.request_engine.get(url)
                if resp and resp.get("text"):
                    links = self._extract_links(target, resp["text"])
                    discovered.extend(links)
            except Exception:
                pass
        return list(set(discovered))

    def _extract_links(self, target: str, html: str) -> List[str]:
        base_domain = urlparse(target).netloc
        pattern = r'(?:href|action|src)=["\']([^"\']+)["\']'
        matches = re.findall(pattern, html)
        links = []
        for m in matches:
            if m.startswith("http"):
                if urlparse(m).netloc == base_domain:
                    links.append(m)
            elif m.startswith("/"):
                links.append(urljoin(target, m))
        return links

    def _classify_workflows(self, endpoints: List[str]) -> List[Dict]:
        workflows = []
        for name, keywords in WORKFLOW_KEYWORDS.items():
            matched = [ep for ep in endpoints if any(kw in ep.lower() for kw in keywords)]
            if matched:
                workflows.append({
                    "name": name.upper(),
                    "endpoints": matched,
                    "stage": list(WORKFLOW_KEYWORDS.keys()).index(name) + 1,
                })
        return sorted(workflows, key=lambda x: x["stage"])

    def print_workflow_graph(self, workflows: List[Dict]):
        if not workflows:
            return
        if _RICH:
            console.print("\n[bold cyan]  WORKFLOW GRAPH[/bold cyan]\n")
            stages = [w["name"] for w in workflows]
            for i, stage in enumerate(stages):
                console.print(f"  [green]{stage}[/green]")
                if i < len(stages) - 1:
                    console.print("  [dim]↓[/dim]")
            console.print()
        else:
            print("\n  WORKFLOW GRAPH\n")
            stages = [w["name"] for w in workflows]
            for i, stage in enumerate(stages):
                print(f"  {stage}")
                if i < len(stages) - 1:
                    print("  ↓")
            print()
