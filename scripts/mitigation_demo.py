# File: mitigation_demo.py
import time
from dragonfly_modp import generate_password_element, generate_password_element_fixed

test_passwords = ["password123", "dragonfly"]  # two sample passwords to compare
ap_mac = "AA:BB:CC:DD:EE:FF"
client_mac = "11:22:33:44:55:66"  # using one sample client MAC for this demo

for pwd in test_passwords:
    # Original algorithm timing
    start = time.perf_counter()
    loops, _ = generate_password_element(pwd, client_mac, ap_mac)
    end = time.perf_counter()
    orig_time = (end - start) * 1e6
    # Mitigated algorithm timing
    start = time.perf_counter()
    loops_fixed, _ = generate_password_element_fixed(pwd, client_mac, ap_mac)
    end = time.perf_counter()
    fixed_time = (end - start) * 1e6
    print(f"Password='{pwd}': Original loops={loops}, time={orig_time:.1f} us;  Fixed loops={loops_fixed}, time={fixed_time:.1f} us")
