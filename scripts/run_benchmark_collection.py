#!/usr/bin/env python3

import argparse
from pathlib import Path
import shutil
import os
import subprocess
import datetime

scripts_dir = Path(__file__).parent

parser = argparse.ArgumentParser(description='run a collection of benchmarks and copy the results')

parser.add_argument('benchmarks', metavar='BENCHMARK', type=Path, nargs='+', help='a benchmark in the collection')
parser.add_argument('-o', '--output', type=Path, required=True, help="the path where the output of the benchmarks will be stored")
args = parser.parse_args()

run_timestamp = datetime.datetime.now()

run_dir = args.output.joinpath(f"run_" + run_timestamp.strftime("%S-%M-%H_%d-%m-%Y"))

for benchmark in args.benchmarks:
    subprocess.run(["make", f"BENCHMARK_PATH={benchmark}", "experiments/single_page_size/layout2mb"], check=True)
    shutil.copytree("experiments/single_page_size/layout2mb", run_dir.joinpath(benchmark.name))
    subprocess.run(["make", "clean"], check=True)
