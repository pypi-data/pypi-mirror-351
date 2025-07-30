"""
UUID generation and management utilities.
"""

import uuid


def generate_uuid() -> str:
    """
    Generate a new UUID string.

    Returns:
    - A newly generated UUID as a string
    """
    return str(uuid.uuid4())
