"""
Account Simulator
Generates synthetic account datasets for lab enumeration testing.
"""

import random
import string
from typing import List, Dict


def generate_email(domain: str = "testlab.local") -> str:
    prefix = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"{prefix}@{domain}"


def generate_account(uid: int = None) -> Dict:
    uid = uid or random.randint(1000, 99999)
    return {
        "user_id": uid,
        "email": generate_email(),
        "username": f"user_{uid}",
        "google_id": "g_" + "".join(random.choices(string.digits, k=12)),
        "fb_id": "fb_" + "".join(random.choices(string.digits, k=10)),
        "sid": "133" + "".join(random.choices(string.digits, k=10)),
    }


def generate_accounts(count: int = 50) -> List[Dict]:
    return [generate_account(uid=i) for i in range(1, count + 1)]


def save_accounts(accounts: List[Dict], path: str = "accounts.json") -> str:
    import json
    with open(path, "w") as f:
        json.dump(accounts, f, indent=2)
    return path
