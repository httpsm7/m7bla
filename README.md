# m7bla — Business Logic Abuse Framework

```
███╗   ███╗ ███████╗ ██████╗ ██╗      █████╗
████╗ ████║ ██╔════╝██╔════╝ ██║     ██╔══██╗
██╔████╔██║ █████╗  ██║  ███╗██║     ███████║
██║╚██╔╝██║ ██╔══╝  ██║   ██║██║     ██╔══██║
██║ ╚═╝ ██║ ███████╗╚██████╔╝███████╗██║  ██║
╚═╝     ╚═╝ ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
```

**Author:** Sharlix | Milkyway Intelligence  
**Version:** 1.0.0  
**Platform:** Kali Linux / Python 3.8+

> For authorized / lab testing only.

---

## Install

```bash
git clone https://github.com/httpsm7/m7bla
cd m7bla
chmod +x install.sh
./install.sh
```

## Usage

```bash
# Full scan
./m7bla -t https://target.com

# With Burp proxy
./m7bla -t https://target.com --proxy http://127.0.0.1:8080

# Quick scan (IDOR + rate limit only)
./m7bla -t https://target.com --mode quick

# Single module
./m7bla -t https://target.com --mode idor
./m7bla -t https://target.com --mode payment
./m7bla -t https://target.com --mode race
./m7bla -t https://target.com --mode recharge
./m7bla -t https://target.com --mode coupon
./m7bla -t https://target.com --mode ratelimit

# Show all attack scenarios
./m7bla --scenarios
```

## Scan Phases (Full Mode)

| Phase | Module | Tests |
|-------|--------|-------|
| 1 | Workflow Mapper | Crawl, path probe, endpoint classification |
| 2 | Parameter Discovery | Form params, JSON keys extraction |
| 3 | Logic Abuse | IDOR, coupon abuse, rate limit bypass |
| 4 | Payment & Recharge | Amount tampering, negative values, step skip |
| 5 | Race Conditions | Concurrent request abuse |
| 6 | Report | HTML + JSON + Markdown output |

## Attack Scenarios

| ID  | Name | Severity |
|-----|------|----------|
| A1  | Amount Tampering via Recharge | HIGH |
| A2  | Payment Step Skip | HIGH |
| A3  | Parallel Recharge Race Condition | HIGH |
| A4  | Coupon Code Reuse | MEDIUM |
| A5  | Negative Value Injection | HIGH |
| A6  | IDOR on User Profile | HIGH |
| A7  | Payment Response Tampering | HIGH |
| A8  | Rate Limit Bypass on Login | MEDIUM |
| A9  | Wallet Balance Overflow | MEDIUM |
| A10 | Duplicate Transaction Replay | HIGH |

## Reports

Reports saved to `./reports/` in 3 formats:
- `m7bla_report_<timestamp>.html` — Cyberpunk dashboard
- `m7bla_report_<timestamp>.json` — Machine-readable
- `m7bla_report_<timestamp>.md` — Markdown

## File Structure

```
m7bla/
├── cli/
│   └── main.py          ← Entry point
├── core/
│   ├── engine.py        ← Orchestrator
│   ├── workflow_mapper.py
│   ├── request_engine.py
│   ├── attack_scenarios.py
│   └── report_engine.py
├── modules/
│   ├── idor_engine.py
│   ├── payment_logic.py
│   ├── recharge_logic.py
│   ├── race_engine.py
│   ├── coupon_abuse.py
│   └── rate_limit_test.py
├── ui/
│   ├── banners.py
│   ├── animations.py
│   └── progress_ui.py
├── generators/
│   └── sid_generator.py
├── reports/
├── install.sh
├── requirements.txt
└── README.md
```
