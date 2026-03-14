"""
ID Generator
Generates sequential and random IDs for IDOR testing.
"""

import random
import string
import uuid
from typing import List


def generate_sequential(start: int = 1, count: int = 100) -> List[int]:
    return list(range(start, start + count))


def generate_random_numeric(length: int = 8, count: int = 100) -> List[str]:
    return ["".join(random.choices(string.digits, k=length)) for _ in range(count)]


def generate_uuids(count: int = 50) -> List[str]:
    return [str(uuid.uuid4()) for _ in range(count)]


def generate_alphanumeric(length: int = 10, count: int = 100) -> List[str]:
    chars = string.ascii_lowercase + string.digits
    return ["".join(random.choices(chars, k=length)) for _ in range(count)]
