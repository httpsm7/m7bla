"""
SID Generator
Generates synthetic subscriber IDs for lab testing.
"""

import random
import string
from typing import List

PREFIXES = ["133", "620", "132", "155", "170", "171", "172", "173", "174", "175"]


def generate_sid(prefix: str = None) -> str:
    """Generate a single SID."""
    pfx = prefix or random.choice(PREFIXES)
    digits = "".join(random.choices(string.digits, k=10))
    return pfx + digits


def generate_sids(count: int = 100, prefix: str = None) -> List[str]:
    """Generate a list of SIDs."""
    return [generate_sid(prefix) for _ in range(count)]


def save_sids(sids: List[str], output_path: str = "sids.txt"):
    """Save SIDs to a file."""
    with open(output_path, "w") as f:
        f.write("\n".join(sids))
    return output_path
