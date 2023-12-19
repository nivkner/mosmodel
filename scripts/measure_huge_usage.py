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
    info = {}
    with meminfo.open() as f:
        for line in f:
            parts = line.split()
            if parts[0] == "AnonHugePages:":
                assert(parts[2] == "kB") # to catch if the units can change
                info['collapsed_huge'] = int(parts[1]) >> 11 # save as huge pages (assume 2MB only)
            elif parts[0] == "HugePages_Total:":
                info['reserved_huge'] = info.setdefault('reserved_huge', 0) + int(parts[1])
            elif parts[0] == "HugePages_Free:":
                info['reserved_huge'] = info.setdefault('reserved_huge', 0) - int(parts[1])
    info['total_huge'] = info['collapsed_huge'] + info['reserved_huge']
    return info

def measure():
    init_huge_mem = sample_huge_mem()
    print(f'Measured initial value: {init_huge_mem}', file=sys.stderr)
    max_huge_mem = init_huge_mem
    global sampling
    while sampling:
        new_huge_mem = sample_huge_mem()
        max_huge_mem = {key: max(value, new_huge_mem[key]) for (key, value) in max_huge_mem.items()}
        time.sleep(1)

    print(f'Measured maximal values: {max_huge_mem}', file=sys.stderr)
    max_huge_mem_diff = {key: value - init_huge_mem[key] for (key, value) in max_huge_mem.items()}
    output = Path("./max_huge_mem.out")
    output.write_text("".join(f"{key},{value}\n" for (key, value) in max_huge_mem_diff.items()))

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    measure()
