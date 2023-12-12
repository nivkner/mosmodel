#!/usr/bin/env python3

import argparse
from pathlib import Path
import shutil

scripts_dir = Path(__file__).parent

parser = argparse.ArgumentParser(description='generate a benchmark for mosmodel using a custom allocator')

parser.add_argument('-b', '--base', type=Path, required=True, help="the path to the mosmodel benchmark on the generated benchmark will be based")
parser.add_argument('-o', '--output', type=Path, required=True, help="the path where the generated benchmark will be created")
parser.add_argument('-a', '--allocator', type=Path, help="the path to the custom allocator used to backing allocations with huge pages")
parser.add_argument('-t', '--thp', action='store_true', help="flag to run the command with THP enabled")
parser.add_argument('-l', '--limit', type=int, default=0, help="maximum number of bytes that can be backed by huge pages")
parser.add_argument('-c', '--choices', type=str, default="", help="a comma delimited list of hex numbers representing the allocations to be backed by huge pages")
parser.add_argument('-r', '--rss', type=str, default="", help="a comma delimited list of the number of bytes used each choice in order")
args = parser.parse_args()

custom_allocator = f"./{args.allocator.name}" if args.allocator is not None else ""

env = f"""
MALLOC_LOG=0
MLOG_MODE=4
MLOG_CAPACITY={args.limit}
MLOG_CONTEXT={args.choices}
MLOG_RSS={args.rss}
LD_PRELOAD={custom_allocator}
"""

shutil.copytree(args.base, args.output)
shutil.move(args.output.joinpath("run.sh"), args.output.joinpath("real_run.sh"))
shutil.copy(scripts_dir.joinpath("run_wrapper.sh"), args.output.joinpath("run.sh"))

assert not args.output.joinpath("env.sh").exists()
args.output.joinpath("env.sh").write_text(env)

if args.allocator is not None:
    shutil.copy(args.allocator, args.output)
