# File: dragonfly_modp.py
import hashlib, hmac, binascii, random
from hashlib import pbkdf2_hmac

# MODP Group-22 parameters (1024-bit prime and generator, 160-bit subgroup order):contentReference[oaicite:6]{index=6}:contentReference[oaicite:7]{index=7}
P = int(
    "B10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C6"
    "9A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C0"
    "13ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD70"
    "98488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0"
    "A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708"
    "DF1FB2BC2E4A4371", 16)
G = int(
    "A4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507F"
    "D6406CFF14266D31266FEA1E5C41564B777E690F5504F213"
    "160217B4B01B886A5E91547F9E2749F4D7FBD7D3B9A92EE1"
    "909D0D2263F80A76A6A24C087A091F531DBF0A0169B6A28A"
    "D662A4D18E73AFA32D779D5918D08BC8858F4DCEF97C2A24"
    "855E6EEB22B3B2E5", 16)
Q = int("F518AA8781A8DF278ABA4E7D64B7CB9D49462353", 16)  # 160-bit prime order of the subgroup

def mac_str_to_bytes(mac_str: str) -> bytes:
    """Convert MAC address string (e.g. 'AA:BB:CC:DD:EE:FF') to 6-byte binary representation."""
    return bytes.fromhex(mac_str.replace(':', ''))

def generate_password_element(password: str, client_mac: str, ap_mac: str):
    """
    Compute the Password Element (PE) for the given password and MAC addresses using 
    the original Dragonfly hunting-and-pecking algorithm:contentReference[oaicite:8]{index=8}:contentReference[oaicite:9]{index=9}.
    
    Returns a tuple (iterations, pe_value). `iterations` is the number of loop iterations 
    used, and `pe_value` is the resulting password element (an integer modulo P).
    """
    pwd_bytes = password.encode('utf-8')
    client_bytes = mac_str_to_bytes(client_mac)
    ap_bytes = mac_str_to_bytes(ap_mac)
    # Loop counter from 1 up to 255 (since probability of needing >255 is almost zero:contentReference[oaicite:10]{index=10})
    for counter in range(1, 256):
        # 1. Compute BASE = SHA512(password || client_mac || ap_mac || counter):contentReference[oaicite:11]{index=11}
        counter_byte = counter.to_bytes(1, 'big')  # single byte for counter
        base = hashlib.sha512(pwd_bytes + client_bytes + ap_bytes + counter_byte).digest()
        # 2. Derive a seed from BASE using PBKDF2 (Password-Based KDF):contentReference[oaicite:12]{index=12}.
        # Use SHA-512 with a single iteration to produce a 1024-bit (128-byte) seed.
        seed = pbkdf2_hmac('sha512', base, b'', 1, dklen=(P.bit_length() + 7) // 8)
        seed_int = int.from_bytes(seed, 'big')
        # 3. Check if seed is a valid candidate: seed < p (prime):contentReference[oaicite:13]{index=13}.
        if seed_int < P:
            # 4. Compute temp = g^seed mod p as a candidate password element.
            pe = pow(G, seed_int, P)
            # 5. Check if temp > 1:contentReference[oaicite:14]{index=14}. (temp == 1 means element is identity, discard)
            if pe > 1:
                # Found a valid Password Element
                return counter, pe
        # If seed_int >= p or pe <= 1, continue to next iteration (counter++ and repeat)
    # If no valid PE found (very unlikely by counter=255:contentReference[oaicite:15]{index=15}), raise an error
    raise RuntimeError("Password element not found within 255 iterations")

def generate_password_element_fixed(password: str, client_mac: str, ap_mac: str, 
                                    Kmin: int = 31, Kmax: int = 255, num_pe: int = 20):
    """
    Compute the Password Element (PE) using the mitigated approach:contentReference[oaicite:16]{index=16}:contentReference[oaicite:17]{index=17}:
      - Always run at least Kmin iterations (default 31) and at most Kmax (255).
      - Collect up to `num_pe` valid PEs in the process (default 20).
      - Once either `num_pe` PEs are found (after reaching at least Kmin loops) or Kmin loops 
        have completed (even if fewer PEs found), stop and return a random PE from the collected set:contentReference[oaicite:18]{index=18}:contentReference[oaicite:19]{index=19}.
    
    Returns a tuple (iterations, pe_value) where iterations is fixed to Kmin or the loop count when num_pe found earlier, 
    and pe_value is one of the valid password elements chosen at random.
    """
    pwd_bytes = password.encode('utf-8')
    client_bytes = mac_str_to_bytes(client_mac)
    ap_bytes = mac_str_to_bytes(ap_mac)
    found_pes = []  # list to store found PEs
    iterations = 0
    for counter in range(1, Kmax + 1):
        iterations = counter
        # Compute base hash and seed (same as above)
        base = hashlib.sha512(pwd_bytes + client_bytes + ap_bytes + counter.to_bytes(1, 'big')).digest()
        seed = pbkdf2_hmac('sha512', base, b'', 1, dklen=(P.bit_length() + 7) // 8)
        seed_int = int.from_bytes(seed, 'big')
        if seed_int < P:
            pe = pow(G, seed_int, P)
            if pe > 1:
                found_pes.append(pe)
                # If we've collected the desired number of PEs and already past minimum iterations, we can stop
                if len(found_pes) >= num_pe and counter >= Kmin:
                    break
        # If we've reached the minimum required loops and haven't found `num_pe` yet, we still stop at Kmin:contentReference[oaicite:20]{index=20}:contentReference[oaicite:21]{index=21}.
        if counter == Kmin:
            # If we haven't hit num_pe by Kmin, we'll stop anyway at Kmin.
            if len(found_pes) > 0:
                break  # stop at Kmin even if num_pe not reached
            # If by some rare chance no PE found by Kmin, we will still break (will use whatever is found up to Kmin, even if none).
            break
    # Choose a random PE from the found list (even if list is smaller than num_pe):contentReference[oaicite:22]{index=22}.
    if not found_pes:
        raise RuntimeError("No password element found by Kmin (unexpected for reasonable Kmin)")
    pe_chosen = random.choice(found_pes)
    return iterations, pe_chosen
