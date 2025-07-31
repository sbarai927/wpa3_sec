import pytest

# adjust this import to point at your actual implementation
from src.dragonfly import hash_to_curve, hash_to_group, curve_params

@pytest.mark.parametrize("password, id1, id2", [
    ("password123", "00:11:22:33:44:55", "66:77:88:99:AA:BB"),
    ("s3cr3t!",     "AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"),
])
def test_hash_to_curve_produces_on_curve(password, id1, id2):
    """
    For a couple of sample inputs ensure hash_to_curve returns a point on the
    chosen elliptic curve (i.e. satisfies y^2 = x^3 + a x + b mod p).
    """
    P = hash_to_curve(password, id1, id2)
    assert isinstance(P, tuple) and len(P) == 2
    x, y = P
    p, a, b = curve_params()
    # curve equation: y^2 mod p == (x^3 + a*x + b) mod p
    left  = pow(y, 2, p)
    right = (pow(x, 3, p) + a * x + b) % p
    assert left == right

def test_hash_to_group_small_example():
    """
    If you have a tiny toy MODP group in your code, test against that
    known example.  Otherwise just assert you get an integer between 2 and p-1.
    """
    password = "letmein"
    id1 = id2 = "00:00:00:00:00:00"
    G = hash_to_group(password, id1, id2)
    p, q, _ = curve_params(group="MODP")    # however you expose those
    assert 1 < G < p
