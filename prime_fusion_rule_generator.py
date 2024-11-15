# prime_fusion_rule_generator.py

"""
Prime Fusion Rule Generator

This script generates a sequence of fusion rules for constructing prime numbers in sequence.
Each rule specifies how to create the next prime number, p[n+1], by "fusing" two smaller primes.

### Fusion Rules and Logic:
1. **Prime Pairing**: To generate each prime number p[n+1], we find two smaller primes (one current and one fusion partner)
   whose sum either equals or nearly reaches p[n+1].
   
2. **Gap Analysis**:
   - The gap between the current prime, p[n], and the next prime, p[n+1], is calculated as: 
     `prime_gap = p[n+1] - p[n]`.
   - We then find the smallest available prime that is greater than or equal to this `prime_gap`.
   
3. **Fusion Partner Selection**:
   - If `p1` (the smallest prime) is greater than or equal to `prime_gap`, it becomes the fusion partner.
   - If `p1` is too small, we try the next smallest prime, and so on, until a suitable fusion partner is found.
   
4. **Remainder Calculation**:
   - In cases where the selected prime pair (current prime + fusion partner) exactly equals p[n+1], no remainder is needed.
   - If the pair sum is less than p[n+1], the remainder is calculated as `remainder = p[n+1] - (current prime + fusion partner)`.
   - The remainder is chosen as the largest prime smaller than the fusion partner.

5. **Output Format**:
   - Each fusion rule is generated as a tuple of the form:
     ```
     ((current_prime, fusion_partner), next_prime, remainder)
     ```
   - For example, `(('p3', 'p1'), 'p4', None)` means `p3 + p1 = p4` with no remainder.

### Special Case:
- The first rule is hardcoded as `(('p1', 'p1'), 'p2', None)` to initialize the sequence.

"""

import json

# Replace the dictionary with a list of primes
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
          73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 
          157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 
          239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 
          331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 
          421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 
          509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 
          613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 
          709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 
          821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 
          919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013, 1019, 
          1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097, 
          1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181, 1187, 1193, 1201, 
          1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277, 1279, 1283, 1289, 1291, 
          1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361, 1367, 1373, 1381, 1399, 1409, 
          1423, 1427, 1429, 1433, 1439, 1447, 1451, 1453, 1459, 1471, 1481, 1483, 1487, 
          1489, 1493, 1499, 1511, 1523, 1531, 1543, 1549, 1553, 1559, 1567, 1571, 1579, 
          1583, 1597, 1601]

def generate_fusion_rules(primes):
    # Initiate the first rule
    fusion_rules = [(('p1', 'p1'), 'p2', None)]

    for i in range(1, len(primes) - 1):
        current_prime_value = primes[i]
        next_prime_value = primes[i + 1]
        current_prime_name = f"p{i + 1}"
        next_prime_name = f"p{i + 2}"

        # Calculate the gap between the current and the next prime
        prime_gap = next_prime_value - current_prime_value

        # Find the smallest prime (fusion_partner) that is greater than or equal to the prime gap
        fusion_partner = None
        remainder_name = None

        for j in range(len(primes)):
            if primes[j] >= prime_gap:
                fusion_partner = (f"p{j + 1}", primes[j])
                remainder_name = f"p{j}" if j > 0 else None
                break

        # Add the fusion rule in the specified format
        fusion_rules.append(((current_prime_name, fusion_partner[0]), next_prime_name, remainder_name))

    return fusion_rules

# Generate the fusion rules
rules = generate_fusion_rules(primes)

# Generate the fusion rules
fusion_rules = generate_fusion_rules(primes)

# Save the fusion rules to rules.json
with open("rules.json", "w") as f:
    json.dump(fusion_rules, f)

print("Fusion rules have been saved to rules.json")