#!/usr/bin/python3
# Generate HW 1 test cases.
# Bart Massey 2021

import random, sys

def bigrand():
    return random.randrange(1, 1 << 64)

for _ in range(int(sys.argv[1])):
    b = bigrand()
    e = bigrand()
    m = bigrand()
    x = pow(b, e, m)
    print("    (")
    print(f"        ({b}, {e}, {m}),")
    print(f"        {x},")
    print("    ),")
