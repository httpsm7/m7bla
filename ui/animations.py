"""
Terminal animation utilities for m7bla.
Gracefully falls back to plain print if 'rich' is not installed.
"""

import time
import sys

try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False
    console = None

STATUS_ICONS = {
    "success": "[✓]",
    "fail":    "[✗]",
    "warn":    "[!]",
    "info":    "[*]",
    "run":     "[→]",
}

def _print(msg: str):
    """Strip rich markup and print plain if rich is unavailable."""
    import re
    clean = re.sub(r'\[/?[^\]]*\]', '', msg)
    print(clean)

def status_line(message: str, kind: str = "info"):
    icon = STATUS_ICONS.get(kind, "[*]")
    if _RICH:
        rich_icons = {
            "success": "[bold green][✓][/bold green]",
            "fail":    "[bold red][✗][/bold red]",
            "warn":    "[bold yellow][!][/bold yellow]",
            "info":    "[bold cyan][*][/bold cyan]",
            "run":     "[bold blue][→][/bold blue]",
        }
        console.print(f"  {rich_icons.get(kind, '[*]')} {message}")
    else:
        print(f"  {icon} {message}")


def typing_effect(lines: list, delay: float = 0.03):
    for line in lines:
        if _RICH:
            console.print(f"  [dim]{line}[/dim]")
        else:
            print(f"  {line}")
        time.sleep(delay)


def loading_animation(label: str = "Loading", steps: int = 8, delay: float = 0.06):
    if _RICH:
        with Progress(
            TextColumn(f"  [cyan]{label}[/cyan]"),
            BarColumn(bar_width=30, style="green", complete_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("", total=steps)
            for _ in range(steps):
                time.sleep(delay)
                progress.advance(task)
        console.print(f"  [bold green][✓][/bold green] [cyan]{label}[/cyan] [dim]done[/dim]")
    else:
        bar = ""
        for i in range(steps):
            bar += "█"
            pct = int((i + 1) / steps * 100)
            print(f"\r  {label}... [{bar:<{steps}}] {pct}%", end="", flush=True)
            time.sleep(delay)
        print(f"\r  [✓] {label} done{' ' * 20}")


def race_animation(url: str, count: int = 10):
    if _RICH:
        console.print(f"\n  [cyan]Race Condition Test → [/cyan][white]{url}[/white]")
        for i in range(1, count + 1):
            time.sleep(0.02)
            console.print(f"    [dim]Request {i:02d} →[/dim] [green]sent[/green]")
    else:
        print(f"\n  Race Condition Test → {url}")
        for i in range(1, count + 1):
            time.sleep(0.02)
            print(f"    Request {i:02d} → sent")
    print()
