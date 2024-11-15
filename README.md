# Prime Number Fusion Simulator

This program is based on the hypothesis that nuclear synthesis may be based on a prime number system.
I invented a set of rules for building prime numbers as follows. 

# The Postulates
* We assume an unlimited supply of p1's [prime numbers 2]
* We assume that two prime numbers may fuse to become the next prime, plus a remainder if the prime gap is larger than (2).
* We postulate that there are no tri-fusion events, ie. fusion can only occur between two primes.

# The Method
* From two p1's we construct p2 as follows: (p1 + p1) --> (p2) i.e. [2 + 2] --> [3]
* With p2 we are able to construct p3: (p2 + p1) = (p3) [3 + 2] --> [5]
* With p3 we are able to construct p4: (p3 + p1) = (p4) [5 + 2] --> [7]
  
Up to this point it is trivial because the prime number gaps equal p1 (2).
The next prime number gap between (p4) and (p5) is (4) and can not be filled with a (p1) (2), ergo we must first first construct another (p3) [5] before this fusion can take place

* With (p4) an (p3) we are able to construct (p5): (p4 + p3) --> (p5) plus a remainder (p2) [7 + 5] --> [11 + 3]
...etc

Following are the first 10 rules...

* [[prime subject, prime partner], prime product, prime remainder]
* [["p1", "p1"], "p2", null]
* [["p2", "p1"], "p3", null]
* [["p3", "p1"], "p4", null]
* [["p4", "p3"], "p5", "p2"]
* [["p5", "p1"], "p6", null]
* [["p6", "p3"], "p7", "p2"]
* [["p7", "p1"], "p8", null] 
* [["p8", "p3"], "p9", "p2"]
* [["p9", "p4"], "p10", "p3"] 
* [["p10", "p1"], "p11", null]


# Rule Generator Program
Creating the prime fusion rules can be complicated and time consuming, therefore I have created a python program which takes a list of primes as input and automatically generates a set of rules. prime_fusion_rule_generator.py

# The Inspiration
The idea for this function comes from the nuclear fusion of elements in stars, where the elementary building block is hydrogen which is fused into the heavier elements. One can imagine the 1-H as (p1) or the real number (2) and 2-H as (p2) or the real number [3], and 3-H as (p3) or the real number [5]. In stellar nuclear synthesis, elements can not be created until their sub components have been made available.
Interestingly we see from the table below that the number of steps required to build a prime number is equal to sum of the ordinals, i.e. after 149 steps we have the following stock;

* 1 x p1
* 1 x p2
* 1 x p5
* 1 x p7
* 3 x p31
* 1 x p32

Which as we can check sums to 149.

We speculate that composite numbers are simply the steps involved in making the primes. It would be interesting to see if this sort of calculation with primes could be extended to a consistent mathematical theory.

# Try the program prime_fusion_cno.py

This program is written in Python Dash-Plotly and it can be run with most installations of Python, from the command line:

> pip install -r requirements.txt
> python prime_fusion_cno.py

# Nuclear synthesis based on primes
Using nothing but a few simple mathematical rules we are able to model nuclear synthesis and show a remarkable correlation between the model and known abundance of the elements. 

This program models a hypothetical fusion process based on nuclear fusion of prime numbers.

# The CNO Fusion cycle
Initially the program produced a good spectrum showing close correlation to isotope abundance, but there appeared to be something missing around p15 to p18 so I added a small set of rules to allow for the fission of (p15), (p17), (p18) as follows:

* [["p15", "p1"], "p12", "p4"],   // CNO-1
* [["p17", "p1"], "p14", "p4"],   // CNO-2
* [["p18", "p1"], "p15", "p4"],   // CNO-3

This correction increased the abundance in the region of C, N and O giving even better correlation.

The justification behind the CNO cycle is that scarcity of large building blocks like p5, p6 and p7 making it more favourable energetically for p15, p17 and p18 to take a step back and fuse with a (p3) rather than sit around and wait for a (p5) or larger prime.

I provided a boolean switch in the program so users can test fusion with and without the CNO cycle.

# Heavy isotope fission
After running the program for a while you will see that heavier isotopes start appearing causing a build up on the right, but we know from experience that heavy isotopes decay, and this I believe is for the same reason, that rather than wait around for the next available building block, it is energetically favourable for the element to fission and try to catch a smaller fusion.

The following fission rules were added

* [["p210", null], "p206", "p4"], // Polonium
* [["p218", null], "p214", "p4"], // Astatine
* [["p222", null], "p218", "p4"], // Radon
* [["p226", null], "p222", "p4"], // Radon
* [["p232", null], "p228", "p4"], // Thorium
* [["p235", null], "p231", "p4"], // Uranium
* [["p238", null], "p234", "p4"], // Uranium
* [["p239", null], "p235", "p4"], // Plutonium
* [["p241", null], "p237", "p4"], // Americium
* [["p244", null], "p240", "p4"], // Curium

This results in the heavier primes decaying, which results in a peak where one would normally expect 214-Bi

# Summary
The goal is to explore the behaviour of a fusion-like system, where elementary particles (represented by prime numbers)
combine in a stochastic manner to produce higher-order primes. Fusion rules govern which prime pairs can combine.

Core Components:
1. **Prime Inventory**: An initial stock of "p1" particles (representing the smallest prime, 2) initiates the fusion. 
   This stock is supplemented by additional "p1" particles each time a fusion succeeds.
   
2. **Fusion Rules**: Each fusion rule describes how two primes combine to form a third prime, sometimes with a byproduct.
   Rules are derived from a structured pattern, where each prime-pair fusion must meet specific gap and combination criteria.
   This results in a deterministic yet complex sequence, progressing from lower primes to higher primes, emulating 
   a sequence similar to nuclear fusion processes in stars. 

3. **Stochastic Process**: The primary while loop uses a stochastic random process to select a fusion rule, however the selection is biased towards primes with more inventory, this makes sense because the probability of collision between to primes is a function of their abundance.

4. **Fission process**
The fission process is also stochastic, but with a condition that scarcity of the next building block must be present in order for fission to occur.

5. **Inventory**: Throughout the entire process the program keep track of the inventory of primes, this includes the remainders and inventory changes as a result of fission

I am absolutely fascinated by how two seemingly unrelated ideas like prime number building and nuclear fusion turns out to have such a correlation. It is by pure chance that I have been interested in prime numbers and nuclear fusion and this idea just seemed to make too much sense. 

Is this the way the Universe works ?

Comments and Feedback please...

Steven Sesselmann



