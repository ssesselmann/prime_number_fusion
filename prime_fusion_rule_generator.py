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

This script supports primes up to `p82` but can be extended for larger ranges by adding primes to the `primes` dictionary.
The generated fusion rules are output as a Python list, making them easy to copy and reuse in other scripts.
"""



def generate_fusion_rules(primes):
    # Initiate the first rule
    fusion_rules = [(('p1', 'p1'), 'p2', None)]

    prime_names = list(primes.keys())
    prime_values = list(primes.values())

    for i in range(1, len(prime_values) - 1):
        current_prime_value     = prime_values[i]
        next_prime_value        = prime_values[i + 1]
        current_prime_name      = prime_names[i]
        next_prime_name         = prime_names[i + 1]

        # Calculate the gap between the current and the next prime
        prime_gap = next_prime_value - current_prime_value

        # Find the smallest prime (fusion_partner) that is greater than or equal to the prime gap
        fusion_partner = None

        for j in range(len(prime_values)):
            if prime_values[j] >= prime_gap:
                fusion_partner = (prime_names[j], prime_values[j])
                remainder_name = prime_names[j - 1] if j > 0 else None
                break

        # Add the fusion rule in the specified format
        fusion_rules.append(((current_prime_name, fusion_partner[0]), next_prime_name, remainder_name))

    return fusion_rules


# Define primes up to p200
primes = {
    "p1": 2, "p2": 3, "p3": 5, "p4": 7, "p5": 11, "p6": 13, "p7": 17,
    "p8": 19, "p9": 23, "p10": 29, "p11": 31, "p12": 37, "p13": 41, "p14": 43,
    "p15": 47, "p16": 53, "p17": 59, "p18": 61, "p19": 67, "p20": 71, "p21": 73,
    "p22": 79, "p23": 83, "p24": 89, "p25": 97, "p26": 101, "p27": 103, "p28": 107,
    "p29": 109, "p30": 113, "p31": 127, "p32": 131, "p33": 137, "p34": 139, "p35": 149,
    "p36": 151, "p37": 157, "p38": 163, "p39": 167, "p40": 173, "p41": 179, "p42": 181,
    "p43": 191, "p44": 193, "p45": 197, "p46": 199, "p47": 211, "p48": 223, "p49": 227,
    "p50": 229, "p51": 233, "p52": 239, "p53": 241, "p54": 251, "p55": 257, "p56": 269,
    "p57": 271, "p58": 277, "p59": 281, "p60": 283, "p61": 293, "p62": 307, "p63": 311,
    "p64": 313, "p65": 317, "p66": 331, "p67": 337, "p68": 347, "p69": 349, "p70": 353,
    "p71": 359, "p72": 367, "p73": 373, "p74": 379, "p75": 383, "p76": 389, "p77": 397,
    "p78": 401, "p79": 409, "p80": 419, "p81": 421, "p82": 431, "p83": 433, "p84": 439,
    "p85": 443, "p86": 449, "p87": 457, "p88": 461, "p89": 463, "p90": 467, "p91": 479,
    "p92": 487, "p93": 491, "p94": 499, "p95": 503, "p96": 509, "p97": 521, "p98": 523,
    "p99": 541, "p100": 547, "p101": 557, "p102": 563, "p103": 569, "p104": 571,
    "p105": 577, "p106": 587, "p107": 593, "p108": 599, "p109": 601, "p110": 607,
    "p111": 613, "p112": 617, "p113": 619, "p114": 631, "p115": 641, "p116": 643,
    "p117": 647, "p118": 653, "p119": 659, "p120": 661, "p121": 673, "p122": 677,
    "p123": 683, "p124": 691, "p125": 701, "p126": 709, "p127": 719, "p128": 727,
    "p129": 733, "p130": 739, "p131": 743, "p132": 751, "p133": 757, "p134": 761,
    "p135": 769, "p136": 773, "p137": 787, "p138": 797, "p139": 809, "p140": 811,
    "p141": 821, "p142": 823, "p143": 827, "p144": 829, "p145": 839, "p146": 853,
    "p147": 857, "p148": 859, "p149": 863, "p150": 877, "p151": 881, "p152": 883,
    "p153": 887, "p154": 907, "p155": 911, "p156": 919, "p157": 929, "p158": 937,
    "p159": 941, "p160": 947, "p161": 953, "p162": 967, "p163": 971, "p164": 977,
    "p165": 983, "p166": 991, "p167": 997, "p168": 1009, "p169": 1013, "p170": 1019,
    "p171": 1021, "p172": 1031, "p173": 1033, "p174": 1039, "p175": 1049, "p176": 1051,
    "p177": 1061, "p178": 1063, "p179": 1069, "p180": 1087, "p181": 1091, "p182": 1093,
    "p183": 1097, "p184": 1103, "p185": 1109, "p186": 1117, "p187": 1123, "p188": 1129,
    "p189": 1151, "p190": 1153, "p191": 1163, "p192": 1171, "p193": 1181, "p194": 1187,
    "p195": 1193, "p196": 1201, "p197": 1213, "p198": 1217, "p199": 1223, "p200": 1229
}

# Generate the fusion rules
rules = generate_fusion_rules(primes)

# Output the rules in a format that's easy to copy as a Python list
print("fusion_rules = [")
for rule in rules:
    print(f"    {rule},")
print("]")
