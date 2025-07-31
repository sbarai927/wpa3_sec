# File: timing_attack_simulation.py
import time, csv
from dragonfly_modp import generate_password_element, generate_password_element_fixed

# Define some test passwords and a fixed AP MAC address (AP's MAC assumed fixed):contentReference[oaicite:28]{index=28} 
test_passwords = ["password123", "hello12345", "dragonfly", "letmein", "guestwifi"]
ap_mac = "AA:BB:CC:DD:EE:FF"  # example AP MAC (fixed for all tests)

# Choose number of spoofed client MAC addresses to test for each password
num_macs_per_password = 10
# Prepare CSV output
csv_filename = "timing_results.csv"
with open(csv_filename, mode='w', newline='') as csvfile:
    fieldnames = ["password", "client_mac", "iterations", "time_us"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for pwd in test_passwords:
        # Generate a set of random client MAC addresses for spoofing attempts
        for i in range(num_macs_per_password):
            # Create a random client MAC (6 bytes). Using Python's random for simulation.
            rand_mac_bytes = [random.randrange(0, 256) for _ in range(6)]
            client_mac = ':'.join(f"{b:02X}" for b in rand_mac_bytes)
            start = time.perf_counter()
            iterations, pe_val = generate_password_element(pwd, client_mac, ap_mac)
            end = time.perf_counter()
            elapsed_us = (end - start) * 1e6  # microseconds
            writer.writerow({
                "password": pwd, 
                "client_mac": client_mac, 
                "iterations": iterations, 
                "time_us": f"{elapsed_us:.1f}"
            })
            # (Optional) print to console for quick feedback
            print(f"[{pwd}] MAC={client_mac} -> loops={iterations}, time={elapsed_us:.1f} us")
print(f"Saved timing data to {csv_filename}")
