def prime_fusion_distribution(target_fusion_steps):
    # Define all primes and potential remainders up to p32 and initialize inventory with zero counts
    primes = [2, 3, 4, 5, 6, 7, 8, 11, 13, 14, 17, 18, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131]
    fusion_counts = {p: 0 for p in primes}

    # Define the fusion rules, with priority on creating heavier primes
    fusion_rules = [
        ((127, 4), 131, 3),         # p31 + p4 -> p32, remainder p3
        ((113, 14), 127, 11),       # p30 + p8 -> p31, remainder p11
        ((109, 4), 113, 3),         # p29 + p4 -> p30, remainder p3
        ((107, 2), 109, None),      # p28 + p1 -> p29
        ((103, 4), 107, 3),         # p27 + p4 -> p28, remainder p3
        ((101, 2), 103, None),      # p26 + p1 -> p27
        ((97, 4), 101, 3),          # p25 + p4 -> p26, remainder p3
        ((89, 8), 97, 7),           # p24 + p6 -> p25, remainder p7
        ((83, 6), 89, 5),           # p23 + p5 -> p24, remainder p5
        ((79, 4), 83, 3),           # p22 + p4 -> p23, remainder p3
        ((73, 6), 79, 5),           # p21 + p5 -> p22, remainder p5
        ((71, 2), 73, None),        # p20 + p1 -> p21
        ((67, 4), 71, 3),           # p19 + p4 -> p20, remainder p3
        ((61, 6), 67, 5),           # p18 + p5 -> p19, remainder p5
        ((59, 2), 61, None),        # p17 + p1 -> p18
        ((53, 6), 59, 5),           # p16 + p5 -> p17, remainder p5
        ((47, 6), 53, 5),           # p15 + p5 -> p16, remainder p5
        ((43, 4), 47, 3),           # p14 + p4 -> p15, remainder p3
        ((41, 2), 43, None),        # p13 + p1 -> p14
        ((37, 4), 41, 3),           # p12 + p4 -> p13, remainder p3
        ((31, 6), 37, 3),           # p11 + p5 -> p12, remainder p3
        ((29, 2), 31, None),        # p10 + p1 -> p11
        ((23, 4), 29, 3),           # p9 + p4 -> p10, remainder p3
        ((19, 3), 23, 2),           # p8 + p2 -> p9, remainder p2
        ((17, 2), 19, None),        # p7 + p1 -> p8
        ((13, 3), 17, 2),           # p6 + p2 -> p7, remainder p2
        ((11, 2), 13, None),        # p5 + p1 -> p6
        ((7, 5), 11, 3),            # p4 + p3 -> p5, remainder p2
        ((5, 2), 7, None),          # p3 + p1 -> p4
        ((3, 2), 5, None),          # p2 + p1 -> p3
        ((2, 2), 3, None)           # p1 + p1 -> p2
    ]

    fusion_step_count = 0  # Only counts actual fusion steps

    # Run the fusion steps until we reach the target number of fusion steps
    while fusion_step_count < target_fusion_steps:
        fusion_occurred = False
        # Attempt to apply fusion rules, prioritizing heaviest first
        for rule in fusion_rules:
            (prime_a, prime_b), result, remainder = rule
            # Check if the rule can be applied
            if fusion_counts[prime_a] >= 1 and fusion_counts[prime_b] >= 1:
                fusion_counts[prime_a] -= 1
                fusion_counts[prime_b] -= 1
                fusion_counts[result] += 1
                if remainder:
                    fusion_counts[remainder] += 1
                fusion_step_count += 1
                print(f"Fusion Step {fusion_step_count}: Fusion {prime_a} + {prime_b} => {result}" + (f", remainder {remainder}" if remainder else ""))
                fusion_occurred = True
                break  # Restart loop to prioritize new inventory for higher primes

        # Only increment p1 if no fusion was possible
        if not fusion_occurred:
            fusion_counts[2] += 1
            print(f"No fusion possible, incremented p1")

    # Collect results, excluding p1 for clarity in final output
    final_distribution = {p: fusion_counts[p] for p in fusion_counts if fusion_counts[p] > 0 and p != 2}
    return final_distribution

# Example usage
target_fusion_steps = 149  # Number of actual fusion steps
distribution = prime_fusion_distribution(target_fusion_steps)
print("\nFinal Prime Distribution after", target_fusion_steps, "fusion steps:")
for prime, count in distribution.items():
    print(f"Prime {prime}: {count}")
