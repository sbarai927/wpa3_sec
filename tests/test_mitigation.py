import pytest
import random

# adjust these imports to your mitigation module
from src.mitigation import hash_to_curve_fixed_time,   \
                           hash_to_group_fixed_time,    \
                           build_pe_database,           \
                           pick_random_pe

@pytest.fixture(autouse=True)
def fix_random_seed(monkeypatch):
    # Make any random calls deterministic for the tests
    monkeypatch.setattr(random, "randint", lambda *args, **kwargs: args[0])

def test_hash_to_curve_fixed_time_iterations():
    """
    Running the mitigated hash_to_curve a few times on the same input
    should always take exactly k iterations.
    """
    password = "password123"
    id1 = "AA:BB:CC:DD:EE:FF"
    id2 = "11:22:33:44:55:66"
    P1, iters1 = hash_to_curve_fixed_time(password, id1, id2)
    P2, iters2 = hash_to_curve_fixed_time(password, id1, id2)
    assert iters1 == iters2  # always same number of loops
    # And of course the element is valid
    from src.dragonfly import curve_params
    p, a, b = curve_params()
    x, y = P1
    assert pow(y,2,p) == (pow(x,3,p) + a*x + b) % p

def test_pe_database_and_random_pick():
    """
    Building a small fixed database of PEs and popping out random entries
    """
    # build a database of 5 PEs for this password
    pw = "hunter2"
    ids = ("00:11:22:33:44:55","66:77:88:99:AA:BB")
    db = build_pe_database(pw, ids, count=5)
    assert len(db) == 5
    # pick_random_pe must return one of them
    chosen = pick_random_pe(db)
    assert chosen in db
