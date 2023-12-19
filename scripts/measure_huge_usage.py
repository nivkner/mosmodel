#!/usr/bin/env python3

import signal
import time
import sys
from pathlib import Path

meminfo = Path("/proc/meminfo")
sampling = True

def handler(signum, frame):
    print(f'Signal handler called with signal {signum}', file=sys.stderr)
    global sampling
    sampling = False

def sample_huge_mem():
    with meminfo.open() as f:
        return next(int(line.split()[1]) for line in f
                    if line.startswith("AnonHugePages:"))

def measure():
    init_huge_mem = sample_huge_mem()
    print(f'Measured initial value of {init_huge_mem} kb', file=sys.stderr)
    max_huge_mem = init_huge_mem
    global sampling
    while sampling:
        max_huge_mem = max(sample_huge_mem(), max_huge_mem)
        time.sleep(1)

    print(f'Measured maximal value of {max_huge_mem} kb', file=sys.stderr)
    max_huge_mem_diff = max_huge_mem - init_huge_mem
    output = Path("./max_huge_mem.out")
    output.write_text(f"{max_huge_mem_diff}\n")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    measure()
