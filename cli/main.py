#!/usr/bin/env python3
"""
m7bla — Business Logic Abuse Framework
CLI Entry Point
Author: Sharlix | Milkyway Intelligence
"""

import argparse
import asyncio
import sys
import os

# Ensure project root is always in sys.path regardless of how the script is invoked
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.chdir(_ROOT)  # ensure relative imports (reports/, etc.) resolve correctly

from core.engine import M7BlaEngine
from ui.banners import print_banner, print_section
from ui.animations import status_line
from core.attack_scenarios import AttackScenarioGenerator


def parse_args():
    parser = argparse.ArgumentParser(
        prog="m7bla",
        description="m7bla — Business Logic Abuse Framework by Sharlix | Milkyway Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/main.py -t https://target.com
  python cli/main.py -t https://target.com --proxy http://127.0.0.1:8080
  python cli/main.py -t https://target.com --mode quick
  python cli/main.py --scenarios
        """
    )

    parser.add_argument(
        "-t", "--target",
        type=str,
        help="Target URL (e.g. https://target.com)",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="HTTP proxy (e.g. http://127.0.0.1:8080)",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "quick", "idor", "payment", "race", "recharge", "coupon", "ratelimit"],
        default="full",
        help="Scan mode (default: full)",
    )
    parser.add_argument(
        "--scenarios",
        action="store_true",
        help="Print all attack scenarios and exit",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    return parser.parse_args()


async def run_mode(engine: M7BlaEngine, mode: str):
    """Run a specific scan mode."""
    if mode == "full":
        await engine.full_scan()
        return

    # Partial mode — map workflows first
    print_section("WORKFLOW MAPPING")
    engine.start_time = __import__("time").time()
    from ui.banners import print_banner
    print_banner()
    engine.workflows, engine.endpoints = await engine.workflow_mapper.map(engine.target)

    print_section(f"MODE: {mode.upper()}")

    if mode == "idor":
        from modules.idor_engine import IDOREngine
        findings = await IDOREngine(engine.request_engine).run(engine.endpoints)
        engine.findings.extend(findings)

    elif mode == "payment":
        from modules.payment_logic import PaymentLogicTester
        findings = await PaymentLogicTester(engine.request_engine).run(engine.endpoints)
        engine.findings.extend(findings)

    elif mode == "race":
        from modules.race_engine import RaceEngine
        findings = await RaceEngine(engine.request_engine).run(engine.endpoints)
        engine.findings.extend(findings)

    elif mode == "recharge":
        from modules.recharge_logic import RechargeLogicTester
        findings = await RechargeLogicTester(engine.request_engine).run(engine.endpoints)
        engine.findings.extend(findings)

    elif mode == "coupon":
        from modules.coupon_abuse import CouponAbuseTester
        findings = await CouponAbuseTester(engine.request_engine).run(engine.endpoints)
        engine.findings.extend(findings)

    elif mode == "ratelimit":
        from modules.rate_limit_test import RateLimitTester
        findings = await RateLimitTester(engine.request_engine).run(engine.endpoints)
        engine.findings.extend(findings)

    elif mode == "quick":
        # Quick: IDOR + rate limit only
        from modules.idor_engine import IDOREngine
        from modules.rate_limit_test import RateLimitTester
        engine.findings.extend(await IDOREngine(engine.request_engine).run(engine.endpoints))
        engine.findings.extend(await RateLimitTester(engine.request_engine).run(engine.endpoints))

    print_section("REPORT")
    engine._generate_report()
    engine.dashboard.print_final_summary(engine.findings, engine.endpoints, engine.workflows)


def main():
    args = parse_args()

    # Scenarios list mode
    if args.scenarios:
        print_banner()
        AttackScenarioGenerator().print_scenarios()
        sys.exit(0)

    if not args.target:
        print("\n  [!] Error: --target is required. Use -h for help.\n")
        sys.exit(1)

    # Validate target
    if not args.target.startswith(("http://", "https://")):
        print("\n  [!] Error: Target must start with http:// or https://\n")
        sys.exit(1)

    engine = M7BlaEngine(
        target=args.target,
        proxy=args.proxy,
        verbose=args.verbose,
    )

    try:
        asyncio.run(run_mode(engine, args.mode))
    except KeyboardInterrupt:
        print("\n\n  [!] Scan interrupted by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n  [!] Fatal error: {e}\n")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
