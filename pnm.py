def prime_fusion_distribution(target_prime):
    # Define primes up to the target and initialize inventory
    primes = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 
        73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 
        157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 
        239, 241, 251, 257, 263, 269, 271, 277, 281
    ]
    fusion_counts = {p: 0 for p in primes}

    # Define fusion rules ordered to prioritize the largest achievable primes
    fusion_rules = [
        ((23, 6), 29, 3), ((2, 2), 3, None), ((3, 2), 5, None), ((5, 2), 7, None),
        ((7, 5), 11, 3), ((11, 2), 13, None), ((13, 3), 17, 2), ((17, 2), 19, None),
        ((19, 3), 23, 2), ((29, 2), 31, None), ((31, 6), 37, 3), ((37, 4), 41, 3),
        ((41, 2), 43, None), ((43, 4), 47, 3), ((47, 6), 53, 5), ((53, 6), 59, 5),
        ((59, 2), 61, None), ((61, 6), 67, 5), ((67, 4), 71, 3), ((71, 2), 73, None),
        ((73, 6), 79, 5), ((79, 4), 83, 3), ((83, 6), 89, 5), ((89, 8), 97, 7),
        ((97, 4), 101, 3), ((101, 2), 103, None), ((103, 4), 107, 3), ((107, 2), 109, None),
        ((109, 4), 113, 3), ((113, 14), 127, 11), ((127, 4), 131, 3), ((131, 3), 137, 2),
        ((137, 2), 139, None), ((139, 4), 149, 3), ((149, 2), 151, None), ((151, 6), 157, 5),
        ((157, 2), 163, None), ((163, 4), 167, 3), ((167, 6), 173, 5), ((173, 4), 179, 3),
        ((179, 2), 181, None), ((181, 6), 191, 5), ((191, 2), 193, None), ((193, 4), 197, 3),
        ((197, 6), 199, 5), ((199, 2), 211, None), ((211, 4), 223, 3), ((223, 2), 227, None),
        ((227, 4), 229, 3), ((229, 6), 233, 5), ((233, 4), 239, 3), ((239, 2), 241, None),
        ((241, 6), 251, 5), ((251, 2), 257, None), ((257, 4), 263, 3), ((263, 6), 269, 5),
        ((269, 4), 271, 3), ((271, 2), 277, None), ((277, 6), 281, 5)
    ]

    # Function to attempt fusion based on available inventory
    def attempt_fusion(target):
        for (prime_a, prime_b), result, remainder in fusion_rules:
            if result == target and fusion_counts[prime_a] >= 1 and fusion_counts[prime_b] >= 1:
                fusion_counts[prime_a] -= 1
                fusion_counts[prime_b] -= 1
                fusion_counts[result] += 1
                if remainder:
                    fusion_counts[remainder] += 1
                print(f"Fused {prime_a} + {prime_b} to create {result}" + (f", remainder {remainder}" if remainder else ""))
                return True
        return False

    fusion_step_count = 0

    # Main fusion loop that moves towards target_prime
    for target in primes[1:]:  # Start from p2 (3), aiming for each target up to the given limit
        while fusion_counts[target] == 0:
            if not attempt_fusion(target):
                # Only manufacture a new p1 (2) if none are available in inventory
                if fusion_counts[2] == 0:
                    fusion_counts[2] += 1
                    print(f"Manufactured new p1 (2); Inventory: {fusion_counts}")
            fusion_step_count += 1
            if target == target_prime and fusion_counts[target] > 0:
                break

    # Display final distribution and total fusion steps
    final_distribution = {p: fusion_counts[p] for p in fusion_counts if fusion_counts[p] > 0}
    print("\nFinal Prime Distribution after achieving target prime", target_prime)
    print(f"Total fusion steps: {fusion_step_count}")
    return final_distribution

# Example run to achieve target prime 29
distribution = prime_fusion_distribution(29)
for prime, count in distribution.items():
    print(f"Prime {prime}: {count}")
