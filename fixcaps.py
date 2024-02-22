import sys
from pathlib import Path

def fixpath(p):
    if not str(p).islower():
        result = str(p).lower()
        p.rename(result)
        return Path(result)
    return p

def fixcaps(d):
    for p in d.iterdir():
        if p.is_file():
            fixpath(p)
        elif p.is_dir():
            p0 = fixpath(p)
            fixcaps(p0)

fixcaps(Path(sys.argv[1]))
