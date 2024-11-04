def prime_fusion_distribution(steps):
    # Define the primes in the sequence
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131]
    fusion_counts = {p: 0 for p in primes}
    fusion_counts[2] = 1  # Start with a single p1 (2), incrementing each step

    # Define fusion rules (source primes, resulting prime, remainder if any)
    fusion_rules = [
        ((2, 2), 3, None),       # 2 + 2 -> 3
        ((3, 2), 5, None),       # 3 + 2 -> 5
        ((5, 2), 7, None),       # 5 + 2 -> 7
        ((7, 5), 11, 3),         # 7 + 5 -> 11, remainder 3
        ((11, 2), 13, None),     # 11 + 2 -> 13
        ((13, 3), 17, 2),        # 13 + 3 -> 17, remainder 2
        ((17, 2), 19, None),     # 17 + 2 -> 19
        ((19, 3), 23, 2),        # 19 + 3 -> 23, remainder 2
        ((23, 4), 29, 3),        # 23 + 4 -> 29, remainder 3
        ((29, 2), 31, None),     # 29 + 2 -> 31
        ((31, 6), 37, 3),        # 31 + 6 -> 37, remainder 3
        # Additional rules can be added here for higher primes
    ]

    # Function to apply a fusion rule
    def apply_rule(rule, step):
        (prime_a, prime_b), result, remainder = rule
        if fusion_counts[prime_a] >= 1 and fusion_counts[prime_b] >= 1:
            fusion_counts[prime_a] -= 1
            fusion_counts[prime_b] -= 1
            fusion_counts[result] += 1
            if remainder:
                fusion_counts[remainder] += 1
            print(f"Step {step}: Completed Prime {result}")
            return True
        return False

    # Run the fusion steps
    for step in range(1, steps + 1):
        fusion_occurred = True
        while fusion_occurred:
            fusion_occurred = False
            for rule in fusion_rules:
                if apply_rule(rule, step):
                    fusion_occurred = True

        # Increment p1 supply by 1 each step
        fusion_counts[2] += 1

    # Filter out primes with zero counts for a clean output
    final_distribution = {p: fusion_counts[p] for p in fusion_counts if fusion_counts[p] > 0}
    return final_distribution

# Example usage
steps = 150  # Number of steps for comparison
distribution = prime_fusion_distribution(steps)
print("\nFinal Prime Distribution after", steps, "steps:")
for prime, count in distribution.items():
    print(f"Prime {prime}: {count}")
