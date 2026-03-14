"""
m7bla - Business Logic Abuse Framework
Core Engine
Author: Sharlix | Milkyway Intelligence
"""

import asyncio
import time
from pathlib import Path
from typing import Optional

from ui.banners import print_banner, print_section
from ui.animations import loading_animation, typing_effect, status_line
from ui.progress_ui import ScanDashboard
from core.workflow_mapper import WorkflowMapper
from core.request_engine import RequestEngine
from core.attack_scenarios import AttackScenarioGenerator
from core.report_engine import ReportEngine
from modules.recharge_logic import RechargeLogicTester
from modules.payment_logic import PaymentLogicTester
from modules.idor_engine import IDOREngine
from modules.race_engine import RaceEngine
from modules.coupon_abuse import CouponAbuseTester
from modules.rate_limit_test import RateLimitTester


class M7BlaEngine:
    """Core orchestration engine for m7bla."""

    def __init__(self, target: str, proxy: Optional[str] = None, verbose: bool = False):
        self.target = target.rstrip("/")
        self.proxy = proxy
        self.verbose = verbose
        self.findings = []
        self.endpoints = []
        self.workflows = []
        self.start_time = None

        # Initialize sub-engines
        self.request_engine = RequestEngine(target, proxy=proxy)
        self.workflow_mapper = WorkflowMapper(self.request_engine)
        self.scenario_gen = AttackScenarioGenerator()
        self.report_engine = ReportEngine()
        self.dashboard = ScanDashboard(target)

    async def full_scan(self):
        """Run full automated scan pipeline."""
        self.start_time = time.time()
        print_banner()
        loading_animation("Initializing modules")

        typing_effect([
            "[*] Target: " + self.target,
            "[*] Mode: Full Business Logic Scan",
            "[*] Author: Sharlix | Milkyway Intelligence",
        ])

        print_section("PHASE 1: WORKFLOW MAPPING")
        await self._phase_workflow_mapping()

        print_section("PHASE 2: PARAMETER DISCOVERY")
        await self._phase_parameter_discovery()

        print_section("PHASE 3: LOGIC ABUSE TESTING")
        await self._phase_logic_testing()

        print_section("PHASE 4: PAYMENT & RECHARGE TESTING")
        await self._phase_payment_testing()

        print_section("PHASE 5: RACE CONDITION TESTING")
        await self._phase_race_testing()

        print_section("PHASE 6: REPORT GENERATION")
        self._generate_report()

        self.dashboard.print_final_summary(self.findings, self.endpoints, self.workflows)

    async def _phase_workflow_mapping(self):
        status_line("Crawling application...", "info")
        self.workflows, self.endpoints = await self.workflow_mapper.map(self.target)
        status_line(f"Discovered {len(self.endpoints)} endpoints", "success")
        status_line(f"Mapped {len(self.workflows)} workflows", "success")
        self.workflow_mapper.print_workflow_graph(self.workflows)

    async def _phase_parameter_discovery(self):
        status_line("Extracting parameters from endpoints...", "info")
        params = await self.request_engine.discover_parameters(self.endpoints)
        status_line(f"Found {len(params)} unique parameters", "success")
        return params

    async def _phase_logic_testing(self):
        # IDOR
        idor = IDOREngine(self.request_engine)
        idor_findings = await idor.run(self.endpoints)
        self.findings.extend(idor_findings)

        # Coupon abuse
        coupon = CouponAbuseTester(self.request_engine)
        coupon_findings = await coupon.run(self.endpoints)
        self.findings.extend(coupon_findings)

        # Rate limit
        rate = RateLimitTester(self.request_engine)
        rate_findings = await rate.run(self.endpoints)
        self.findings.extend(rate_findings)

    async def _phase_payment_testing(self):
        recharge = RechargeLogicTester(self.request_engine)
        recharge_findings = await recharge.run(self.endpoints)
        self.findings.extend(recharge_findings)

        payment = PaymentLogicTester(self.request_engine)
        payment_findings = await payment.run(self.endpoints)
        self.findings.extend(payment_findings)

    async def _phase_race_testing(self):
        race = RaceEngine(self.request_engine)
        race_findings = await race.run(self.endpoints)
        self.findings.extend(race_findings)

    def _generate_report(self):
        elapsed = time.time() - (self.start_time or time.time())
        report_path = self.report_engine.generate(
            target=self.target,
            findings=self.findings,
            endpoints=self.endpoints,
            workflows=self.workflows,
            elapsed=elapsed,
        )
        status_line(f"Report saved: {report_path}", "success")
