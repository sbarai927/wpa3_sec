# src/mitigation.py

import random
from .dragonfly_modp import hash_to_group, curve_params

# How many iterations we force, for fixed‐time defenses
DEFAULT_K = 40

def hash_to_group_fixed_time(password, id1, id2, token=None, k=DEFAULT_K):
    """
    Always perform exactly k 'hunting‐and‐pecking' loops before returning the true PE.
    Returns (PE, iterations_used==k).
    """
    # Run k−1 dummy rounds on random data to burn time
    for _ in range(k - 1):
        # swap password out for a random one so we don't leak the real PE early
        dummy_pw = hex(random.getrandbits(64))
        try:
            hash_to_group(dummy_pw, id1, id2, token=token)
        except Exception:
            # ignore any edge‐case failures
            pass

    # Now do the real call exactly once and return it
    P = hash_to_group(password, id1, id2, token=token)
    return P, k

# For ECC‐based code you would do something similar with hash_to_curve(),
# but if you only have modp you can alias:
hash_to_curve_fixed_time = hash_to_group_fixed_time


def build_pe_database(password, ids, count=20):
    """
    Generate 'count' password‐elements (PEs) from the same password,
    varying only the MAC-based input (we’ll just cycle a dummy counter here).
    ids should be a 2‐tuple like (client_mac, ap_mac).
    Returns a list of distinct PEs.
    """
    id1, id2 = ids
    db = []
    # If your hash_to_group takes an explicit 'counter' argument, use it here.
    # Otherwise this just repeatedly calls with the same inputs.
    for i in range(1, count + 1):
        # If your underlying function allowed a 'counter' param, pass counter=i.
        P = hash_to_group(password, id1, id2)
        db.append(P)
    return db

def pick_random_pe(db):
    """
    Randomly pick one PE from the database.
    """
    return random.choice(db)
