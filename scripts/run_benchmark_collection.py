#!/usr/bin/env python3

import argparse
from pathlib import Path
import shutil
import os
import subprocess
import datetime
from summarize_benchmarks import summarize_benchmarks

scripts_dir = Path(__file__).parent

parser = argparse.ArgumentParser(description='run a collection of benchmarks and copy the results')

parser.add_argument('benchmarks', metavar='BENCHMARK', type=Path, nargs='+', help='a benchmark in the collection')
parser.add_argument('-o', '--output', type=Path, required=True, help="the path where the output of the benchmarks will be stored")
parser.add_argument('-s', '--summary', type=Path, help="the path where the summary of the benchmarks will be stored")
parser.add_argument('-i', '--iterations', type=int, default=3, help="the number of iterations done per benchmark")
parser.add_argument('-p', '--progressive', type=str, metavar="SIG", help="add results to an existing analysis with the matching sig if one exists")
args = parser.parse_args()

signature = args.progressive if args.progressive is not None else datetime.datetime.now().strftime("%S-%M-%H_%d-%m-%Y")

run_dir = args.output.joinpath(f"run_" + signature)

for benchmark in args.benchmarks:
    run_benchmark = run_dir.joinpath(benchmark.name)
    top_prev_iter = 0
    if run_benchmark.exists():
        top_prev_iter = max((int(f.name.removeprefix("repeat")) for f in run_benchmark.glob("repeat*")), default=0)
    run_benchmark.mkdir(parents=True, exist_ok=True)

    for n in range(top_prev_iter+1, top_prev_iter + args.iterations + 1):
        tmp_output = "experiments/single_page_size/layout2mb/repeat1"
        subprocess.run(["make", f"BENCHMARK_PATH={benchmark}", tmp_output], check=True)
        shutil.move(tmp_output, run_benchmark.joinpath(f"repeat{n}"))

    shutil.rmtree("experiments/single_page_size/layout2mb")

subprocess.run(["make", "clean"], check=True)

if args.summary is not None:
    summary_file = args.summary.joinpath(run_dir.name + "_summary.csv")
    summarize_benchmarks(run_dir, summary_file)
    print(f"summary is at {summary_file}")
