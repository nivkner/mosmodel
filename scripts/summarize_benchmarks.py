#!/usr/bin/env python3

import argparse
from pathlib import Path
import shutil
import os
import subprocess
import polars as pl

scripts_dir = Path(__file__).parent

parser = argparse.ArgumentParser(description='summarize all of the information gathered by mosmodel on a given run')

parser.add_argument('-i', '--input', type=Path, required=True, help="the path where the results of a run are stored")
parser.add_argument('-o', '--output', type=Path, required=True, help="the path where the summary will be stored")
args = parser.parse_args()

benchmark_dfs = []

for benchmark in args.input.iterdir():
    benchmark_time_df = pl.scan_csv(benchmark.joinpath("repeat*/time.out"), has_header=False, new_columns=["Measure", "Value"])
    benchmark_perf_df = pl.scan_csv(benchmark.joinpath("repeat*/perf.out"), has_header=False, skip_rows=2, new_columns=["Value", "Unit", "Measure"]).select("Measure", pl.col("Value").cast(pl.Float64))
    benchmark_df = pl.concat([benchmark_time_df, benchmark_perf_df])

    benchmark_df = benchmark_df.group_by("Measure").agg(pl.col("Value").mean().alias("Mean"), pl.col("Value").std().alias("StdDev"), pl.lit(benchmark.name).alias("Benchmark"))

    benchmark_dfs.append(benchmark_df)

summary_df = pl.concat(benchmark_dfs)

summary_df.collect(streaming=True).write_csv(args.output.joinpath(args.input.name + "_summary.csv"))
