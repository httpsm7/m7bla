"""
Attack Scenario Generator
Auto-generates business logic attack scenarios.
Gracefully falls back if 'rich' is not installed.
"""

from typing import List, Dict

try:
    from rich.console import Console
    from rich.table import Table
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False

SCENARIOS = [
    {
        "id": "A1",
        "name": "Amount Tampering via Recharge",
        "steps": ["Login", "Navigate to Recharge", "Intercept Request", "Modify amount=100 → amount=1"],
        "targets": ["amount", "price", "total"],
        "severity": "HIGH",
    },
    {
        "id": "A2",
        "name": "Payment Step Skip",
        "steps": ["Login", "Add to Cart", "Skip Payment Endpoint", "Call Confirmation API directly"],
        "targets": ["order_id", "session"],
        "severity": "HIGH",
    },
    {
        "id": "A3",
        "name": "Parallel Recharge Race Condition",
        "steps": ["Login", "Send 50 concurrent recharge requests", "Check balance duplication"],
        "targets": ["wallet", "balance"],
        "severity": "HIGH",
    },
    {
        "id": "A4",
        "name": "Coupon Code Reuse",
        "steps": ["Login", "Apply coupon", "Note coupon_code", "Re-apply on new order"],
        "targets": ["coupon", "discount_code", "promo"],
        "severity": "MEDIUM",
    },
    {
        "id": "A5",
        "name": "Negative Value Injection",
        "steps": ["Login", "Recharge endpoint", "Set amount=-100", "Check if balance increases"],
        "targets": ["amount", "quantity"],
        "severity": "HIGH",
    },
    {
        "id": "A6",
        "name": "IDOR on User Profile",
        "steps": ["Login as User A", "Note user_id", "Change user_id to User B", "Access profile"],
        "targets": ["user_id", "uid", "account_id"],
        "severity": "HIGH",
    },
    {
        "id": "A7",
        "name": "Payment Response Tampering",
        "steps": ["Intercept payment callback", "Modify status=failed → status=success", "Check order completion"],
        "targets": ["status", "payment_status", "txn_status"],
        "severity": "HIGH",
    },
    {
        "id": "A8",
        "name": "Rate Limit Bypass on Login",
        "steps": ["Send 1000 login requests", "Vary IP header", "Check for lockout"],
        "targets": ["X-Forwarded-For", "username", "email"],
        "severity": "MEDIUM",
    },
    {
        "id": "A9",
        "name": "Wallet Balance Overflow",
        "steps": ["Login", "Set amount=999999999", "Check if negative balance or overflow"],
        "targets": ["amount", "wallet_amount"],
        "severity": "MEDIUM",
    },
    {
        "id": "A10",
        "name": "Duplicate Transaction Replay",
        "steps": ["Capture valid recharge request", "Replay same request 5 times", "Check balance increment"],
        "targets": ["txn_id", "request_id"],
        "severity": "HIGH",
    },
]


class AttackScenarioGenerator:
    def get_all(self) -> List[Dict]:
        return SCENARIOS

    def get_by_severity(self, severity: str) -> List[Dict]:
        return [s for s in SCENARIOS if s["severity"] == severity.upper()]

    def get_for_endpoints(self, endpoints: List[str]) -> List[Dict]:
        matched = []
        for scenario in SCENARIOS:
            for target in scenario["targets"]:
                for ep in endpoints:
                    if target.lower() in ep.lower():
                        if scenario not in matched:
                            matched.append(scenario)
        return matched or SCENARIOS

    def print_scenarios(self):
        if _RICH:
            table = Table(
                title="[bold cyan]Attack Scenarios — m7bla[/bold cyan]",
                border_style="cyan", show_lines=True,
            )
            table.add_column("ID",       style="yellow",  width=5)
            table.add_column("Name",     style="white",   width=42)
            table.add_column("Severity", style="bold",    width=10)
            table.add_column("Targets",  style="dim",     width=32)
            for s in SCENARIOS:
                color = "red" if s["severity"] == "HIGH" else "yellow"
                table.add_row(
                    s["id"],
                    s["name"],
                    f"[{color}]{s['severity']}[/{color}]",
                    ", ".join(s["targets"]),
                )
            console.print(table)
        else:
            print(f"\n  {'ID':<5} {'Severity':<10} Name")
            print(f"  {'-'*65}")
            for s in SCENARIOS:
                print(f"  {s['id']:<5} {s['severity']:<10} {s['name']}")
            print()
