# Prime Number Fusion Simulator

This program is based on the hypotheseis that nuclear synthesis may be based on a prime number system.
Steven Sesselmann invented a set of rules for building prime numbers as follows. 

# The Postulates
* We assume an unlimited supply of p1's [prime numbers 2]
* We assume that two prime numbers may fuse to become the next prime plus a remainder if the prime gap is larger than (2).
* We postulate that there are no tri-fusion events, ie. fusion only occurs between two primes.

# The Method
* From two p1's we construct p2 as follows: (p1 + p1) --> p2 [2 + 2] --> 3
* With p2 we are able to construct p3: (p2 + p1) = p3 [3 + 2] --> 5
* With p3 we are able to construct p4: (p3 + p1) = p4 [5 + 2] --> 7
  
Up to this point it is trivial because the prime number gaps equal p1 (2).
The next prime number gap between p4 and p5 is (4) and can not be completed with a p1 (2), ergo one must first first construct another p3 (5) before this process can take place

* With p4 an p3 we are able to construct p5: (p4 + p3) --> p5 plus a remainder p2 [7 + 5] --> [11 + 3]
...etc

# Rule Generator Program
Creating the prime fusion rules can be complicated and time consuming, therefore i have created a python program which takes a list of primes as input and automatically generates a set of rules. prime_fusion_rule_generator.py

# The Inspiration
The idea for this function comes from the nuclear fusion of elements in stars, where the elementary building block is hydrogen which is fused into the heavier elements. One can imagine the proton as p1 or the real number (2) and Deuterium as p2 or the real number 3, and Tritium as p3 or the real number (5). In a star as in my program, elements can not be created until their sub components have been made available.
Interestingly we see from the table below that the number of steps required to build a prime number is equal to sum of the ordinals, i.e. after 149 steps we have the following stock;

1 x p1
1 x p2
1 x p5
1 x p7
3 x p31
1 x p32

Which as we can check sums to 149.

One may speculate that composite numbers are simply steps involved in making the primes. It would be interesting to see if this sort of calculation with primes could be extended to a consistent mathematical theory.

# Try the program prime_fusion_dash.py
This program is written in Python Dash-Plotly and it can be run with most instalations of Python, from the command line simply type python prime_fusion_dash.py

# What does the program do?

This program models a hypothetical fusion process inspired by nuclear fusion and prime numbers.
The goal is to explore the behavior of a fusion-like system, where elementary particles (represented by prime numbers)
combine in a stochastic manner to produce higher-order primes. Fusion rules govern which prime pairs can combine, 
and the resulting "fusion products" are constrained by both the primes involved and a Gaussian-weighted selection, 
favoring specific fusion pathways while allowing for stochastic variation. 

Core Components:
1. **Prime Inventory**: An initial stock of "p1" particles (representing the smallest prime, 2) initiates the fusion. 
   This stock is supplemented by additional "p1" particles each time a fusion succeeds.
   
2. **Fusion Rules**: Each fusion rule describes how two primes combine to form a third prime, sometimes with a byproduct.
   Rules are derived from a structured pattern, where each prime-pair fusion must meet specific gap and combination criteria.
   This results in a deterministic yet complex sequence, progressing from lower primes to higher primes, emulating 
   a sequence similar to nuclear fusion processes in stars. 

3. **Gaussian-weighted Fusion**: Fusion steps are not purely random; instead, the rule selection follows a Gaussian 
   distribution centered on a preferred "target" prime. This models real-world fusion probability, where fusion likelihood 
   depends on particle masses. Here, primes closer to the central fusion target have a higher likelihood of being selected.

4. **Stochastic Process**: The primary loop runs a specified number of fusion steps. In each step, an attempt is made to 
   apply a weighted fusion rule. If successful, inventory counts are updated; otherwise, the system attempts another fusion. 
   Successful fusions add one new "p1" particle to simulate continuous particle availability and encourage new reactions.

5. **Output**: After the simulation completes the specified number of fusion steps, the program outputs the final inventory 
   of primes, showing the distribution of "fusion products" generated by the stochastic prime fusion process.

By incorporating Gaussian-weighted selection and a carefully structured fusion rule set, this program provides insights 
into a complex fusion network governed by prime numbers, where order emerges from stochastic interactions within specific rules.

Comments and Feedback please...

Steven Sesselmann


