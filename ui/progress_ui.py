"""
Scan Dashboard — Live progress & final summary UI.
Gracefully falls back to plain print if 'rich' is not installed.
"""

import time
from typing import List, Dict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False
    console = None


class ScanDashboard:
    def __init__(self, target: str):
        self.target = target
        self.start_time = time.time()

    def print_final_summary(self, findings: List[Dict], endpoints: List[str], workflows: List[Dict]):
        elapsed = round(time.time() - self.start_time, 1)
        high   = [f for f in findings if f.get("severity") == "HIGH"]
        medium = [f for f in findings if f.get("severity") == "MEDIUM"]
        low    = [f for f in findings if f.get("severity") == "LOW"]

        if _RICH:
            console.print()
            console.rule("[bold green]  SCAN COMPLETE  [/bold green]", style="green")
            console.print()

            stats = [
                _stat_card("ENDPOINTS", str(len(endpoints)), "cyan"),
                _stat_card("WORKFLOWS", str(len(workflows)), "blue"),
                _stat_card("HIGH",      str(len(high)),      "red"),
                _stat_card("MEDIUM",    str(len(medium)),    "yellow"),
                _stat_card("LOW",       str(len(low)),       "green"),
                _stat_card("TIME",      f"{elapsed}s",       "magenta"),
            ]
            console.print(Columns(stats, equal=True, expand=True))
            console.print()

            if findings:
                table = Table(
                    title="[bold cyan]Findings Summary[/bold cyan]",
                    border_style="cyan", show_lines=True, header_style="bold cyan",
                )
                table.add_column("#",        style="dim",   width=4)
                table.add_column("Severity", style="bold",  width=10)
                table.add_column("Name",     style="white", width=42)
                table.add_column("Endpoint", style="dim",   width=45)

                for i, f in enumerate(findings, 1):
                    sev = f.get("severity", "?")
                    color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(sev, "white")
                    table.add_row(
                        str(i),
                        f"[{color}]{sev}[/{color}]",
                        f.get("name", "Unknown"),
                        f.get("endpoint", "N/A"),
                    )
                console.print(table)
            else:
                console.print("  [dim]No findings recorded.[/dim]")

            console.print()
            console.print("  [bold green][✓][/bold green] [dim]Reports saved to[/dim] [cyan]./reports/[/cyan]")
            console.print()

        else:
            print()
            print("  ══ SCAN COMPLETE ══")
            print(f"  Endpoints : {len(endpoints)}")
            print(f"  Workflows : {len(workflows)}")
            print(f"  HIGH      : {len(high)}")
            print(f"  MEDIUM    : {len(medium)}")
            print(f"  LOW       : {len(low)}")
            print(f"  Time      : {elapsed}s")
            print()
            if findings:
                print(f"  {'#':<4} {'SEV':<8} {'NAME':<40} ENDPOINT")
                print(f"  {'-'*90}")
                for i, f in enumerate(findings, 1):
                    print(f"  {i:<4} {f.get('severity','?'):<8} {f.get('name','Unknown'):<40} {f.get('endpoint','N/A')}")
            else:
                print("  No findings recorded.")
            print()
            print("  [✓] Reports saved to ./reports/")
            print()


def _stat_card(label: str, value: str, color: str) -> "Panel":
    content = Text(f"{value}\n", style=f"bold {color}", justify="center")
    content.append(label, style="dim")
    return Panel(content, border_style=color, padding=(0, 2))
