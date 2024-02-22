#!/usr/bin/python3
# Do basic Rust HW tests
# Bart Massey 2021

import subprocess

def clean():
    subprocess.run("cargo clean".split())

def test(*args, expect=None, expect_fail=False):
    cmd = "cargo run --".split()
    cmd += map(lambda i: str(i), args)
    cmdstr = ' '.join(cmd)

    print("*", cmdstr)

    result = subprocess.run(cmd, capture_output=True, text=True)

    fail = result.returncode != 0
    if fail != expect_fail:
        print("*", cmdstr, "failed")
        print(result.stderr, end="")

    outputs = result.stdout.splitlines()

    if expect is not None:
        if len(outputs) == 0:
            print(f"* no output (expected {expect})")
            return
        printed = False
        if len(outputs) > 1:
            print("* multiline output")
            print(result.stdout, end="")
            printed = True
        try:
            value = int(outputs[-1])
            if value != expect:
                print(f"* incorrect output: expected {expect}, got {value}")
        except:
            print(f"* incorrect output format (expected {expect})")
            if not printed:
                print(result.stdout, end="")

# tests which are expected to succeed
tests = [
    ((2, 20, 17), 16),
    ((65045062, 3346591621, 2050983529), 779460057),
    ((3157249057, 642450257, 1206077675), 793430932),
    ((254442834, 3119054021, 4120472621), 420504248),
    ((3122336194, 303273719, 793557431), 198748694),
    ((1416053226, 1179260608, 3407372052), 2542722756),
    ((269068352, 2097135683, 1813329190), 1693049578),
    ((1783813899, 2524635395, 1047357735), 175031379),
    ((1542361516, 2954997086, 3387843065), 1047688881),
    ((1820089590, 1599001260, 4098703437), 4057801920),
    ((1743817115, 450929719, 3730619216), 1552068307),
    (
        (1341732828632008959, 12768408515469781835, 18005399762946816118),
        8070139731897444595,
    ),
    (
        (10837617410791325984, 13137013005133147062, 5605018205037600787),
        4728720577166425626,
    ),
    (
        (18064532669199020729, 15500302152020561147, 9312413868965145524),
        3595450845471137161,
    ),
    (
        (14689613164221199451, 14762397228096952138, 5907881372731441892),
        1426046069126890597,
    ),
    (
        (8326914581224827294, 2167461000851797207, 14689208968309200292),
        4801727479642737708,
    ),
    (
        (268981107315349922, 456417029603958328, 18401069682983250155),
        14384850073681215016,
    ),
    (
        (11853390956384928778, 3146532905818700109, 4919460523163940097),
        2709805997352629294,
    ),
    (
        (10677856034602798835, 2157009884012462574, 14074388208166156674),
        8566910712206466607,
    ),
    (
        (14961004951911953260, 16261633317446206779, 14865411986035984720),
        10124370943729838960,
    ),
    (
        (200161039751247455, 10154514612069862732, 7055723376328453559),
        6992353223301772651,
    ),
]

# tests which are expected to fail
negative_tests = [
    (2, 4, 8),
    (-1, 0, 8),
    (0, 0, -1),
    (2, 4, 2**64),
    (2**64, 4, 8),
]

for i, o in tests:
    test(*i, expect=o)

for i in negative_tests:
    test(*i, expect_fail=True)

clean()
