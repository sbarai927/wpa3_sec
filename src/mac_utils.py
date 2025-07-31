# File: mac_utils.py
import random

def random_mac() -> str:
    """Generate a random MAC address string in the format AA:BB:CC:DD:EE:FF."""
    return ':'.join(f"{random.randrange(0,256):02X}" for _ in range(6))
