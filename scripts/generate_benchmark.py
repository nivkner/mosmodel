#!/usr/bin/env python3

import argparse
from pathlib import Path
import shutil
import os

scripts_dir = Path(__file__).parent

parser = argparse.ArgumentParser(description='generate a benchmark for mosmodel using a custom allocator')

parser.add_argument('-b', '--base', type=Path, required=True, help="the path to the mosmodel benchmark on the generated benchmark will be based")
parser.add_argument('-o', '--output', type=Path, required=True, help="the path where the generated benchmark will be created")
parser.add_argument('-a', '--allocator', type=Path, help="the path to the custom allocator used to backing allocations with huge pages")
parser.add_argument('-d', '--description', type=str, help="a string describing the benchmark, for posterity")
parser.add_argument('-t', '--thp', action='store_true', help="flag to run the command with THP enabled")
parser.add_argument('-e', '--env_vars', type=str, nargs='+', default=[], metavar="VAR=VALUE", help="a list of env vars to be passed to the allocator")
parser.add_argument('-r', '--reserve', type=int, help="override the number of huge pages reserved by mosmodel")
args = parser.parse_args()

custom_allocator = f"./{args.allocator.name}" if args.allocator is not None else ""

env_str = "\n".join(args.env_vars)

env_full = f"""
{env_str}
LD_PRELOAD={custom_allocator}
USE_THP={int(args.thp)}
"""

shutil.copytree(args.base, args.output, symlinks=True)
shutil.move(args.output.joinpath("run.sh"), args.output.joinpath("real_run.sh"))
shutil.copy(scripts_dir.joinpath("run_wrapper.sh"), args.output.joinpath("run.sh"))

assert not args.output.joinpath("env.sh").exists()
args.output.joinpath("env.sh").write_text(env_full)

if args.allocator is not None:
    shutil.copy(args.allocator, args.output)

if args.description is not None:
    assert not args.output.joinpath("description.txt").exists()
    args.output.joinpath("description.txt").write_text(args.description)

if args.reserve is not None:
    assert not args.output.joinpath("reserve.cfg").exists()
    args.output.joinpath("reserve.cfg").write_text(f"{args.reserve},0")
