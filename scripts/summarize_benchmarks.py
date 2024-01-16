#!/usr/bin/env python3

import argparse
from pathlib import Path
import shutil
import os
import subprocess
import polars as pl

def summarize_benchmarks(outputs_dir):
    for benchmark in outputs_dir.iterdir():
        df_types = []
        df_types.append(pl.scan_csv(benchmark.joinpath("repeat*/time.out"), has_header=False, new_columns=["Measure", "Value"]))
        df_types.append(pl.scan_csv(benchmark.joinpath("repeat*/perf.out"), has_header=False, skip_rows=2, new_columns=["Value", "Unit", "Measure"]).select("Measure", pl.col("Value").cast(pl.Float64)))
        df_types.append(pl.scan_csv(benchmark.joinpath("repeat*/meminfo.out"), has_header=False, new_columns=["Measure", "Value"], dtypes=[pl.Utf8, pl.Float64]))

        benchmark_df = pl.concat(df_types)

        benchmark_df = benchmark_df.group_by("Measure").agg(pl.col("Value").mean().alias("Mean"), pl.col("Value").std().alias("StdDev"), pl.lit(benchmark.name).alias("Benchmark"))

        benchmark_dfs.append(benchmark_df)

    return pl.concat(benchmark_dfs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='summarize all of the information gathered by mosmodel on a given run')

    parser.add_argument('-i', '--input', type=Path, required=True, help="the path where the results of a run are stored")
    parser.add_argument('-o', '--output', type=Path, required=True, help="the path where the summary will be stored")
    args = parser.parse_args()

    summary_df = summarize_benchmarks(args.input)

    args.output.mkdir(parents=True, exist_ok=True)

    summary_df.collect(streaming=True).write_csv(args.output.joinpath(args.input.name + "_summary.csv"))
