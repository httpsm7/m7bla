"""
Banners and section headers for m7bla.
Gracefully falls back to plain print if 'rich' is not installed.
"""

try:
    from rich.console import Console
    from rich.text import Text
    from rich.align import Align
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False
    console = None

# Hand-crafted ASCII art — M7BLA — verified correct
BANNER = r"""
  ___  ___  ____  _       ___
 |   \/   ||    \| |     / _ \
 | |\/| | || |_) | |    / /_\ \
 | |  | | ||  _ <| |___/ _____ \
 |_|  |_|_||_| \_\____/_/     \_\
   M  7  B  L  A
"""

BANNER_BLOCK = """
  +-+-+-+-+-+-+
  |M|7|B|L|A|!|
  +-+-+-+-+-+-+
"""

def print_banner():
    if _RICH:
        console.print()
        console.print(Align.center(Text(BANNER, style="bold green")))
        info = (
            "[dim]m7bla[/dim] [bold green]Business Logic Abuse Framework[/bold green]\n"
            "[dim]Author:[/dim] [cyan]Sharlix[/cyan]  |  "
            "[dim]Brand:[/dim] [cyan]Milkyway Intelligence[/cyan]\n"
            "[dim]Version:[/dim] [white]1.0.0[/white]  |  "
            "[dim]Use for:[/dim] [yellow]Authorized / Lab Testing Only[/yellow]"
        )
        console.print(Align.center(info))
        console.print()
    else:
        print()
        print(BANNER)
        print("  m7bla — Business Logic Abuse Framework")
        print("  Author: Sharlix  |  Brand: Milkyway Intelligence")
        print("  Version: 1.0.0  |  For Authorized / Lab Testing Only")
        print()


def print_section(title: str):
    if _RICH:
        console.print()
        console.rule(f"[bold cyan]  {title}  [/bold cyan]", style="cyan dim")
        console.print()
    else:
        print()
        print(f"  {'─' * 50}")
        print(f"    {title}")
        print(f"  {'─' * 50}")
        print()
