#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import shutil
import os
import subprocess
import polars as pl

def get_memtier_df_from_json(memtier_json_path):
    with open(memtier_json_path) as json_file:
        js = json.load(json_file)
        bench_stats = js["ALL STATS"]["Totals"]
        bench_stats.pop("Time-Serie")
        percentiles = bench_stats.pop("Percentile Latencies")
        percentiles.pop("Histogram log format")
        bench_stats = {**bench_stats, **({"Latency "+key: val for (key,val) in percentiles.items()})}
        return pl.LazyFrame(bench_stats).melt(variable_name="Measure", value_name="Value")

def summarize_benchmark(benchmark_dir):
    df_types = []
    df_types.append(pl.scan_csv(benchmark_dir.joinpath("repeat*/time.out"), has_header=False, new_columns=["Measure", "Value"]))
    df_types.append(pl.scan_csv(benchmark_dir.joinpath("repeat*/perf.out"), has_header=False, skip_rows=2, new_columns=["Value", "Unit", "Measure"]).select("Measure", pl.col("Value").cast(pl.Float64)))
    df_types.append(pl.scan_csv(benchmark_dir.joinpath("repeat*/meminfo.out"), has_header=False, new_columns=["Measure", "Value"], schema_overrides=[pl.Utf8, pl.Float64]))

    for memtier_json in benchmark_dir.glob("repeat*/bench.json"):
        df_types.append(get_memtier_df_from_json(memtier_json))

    benchmark_df = pl.concat(df_types)

    return benchmark_df.group_by("Measure").agg(pl.col("Value").mean().alias("Mean"), pl.col("Value").std().alias("StdDev"), pl.lit(benchmark_dir.name).alias("Benchmark"))

def summarize_benchmarks(outputs_dir, summary_file):
    summary_df = pl.concat([summarize_benchmark(benchmark_dir) for benchmark_dir in outputs_dir.iterdir()])
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_df.collect(streaming=True).write_csv(summary_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='summarize all of the information gathered by mosmodel on a given run')

    parser.add_argument('-i', '--input', type=Path, required=True, help="the path where the results of a run are stored")
    parser.add_argument('-o', '--output', type=Path, required=True, help="the path where the summary will be stored")
    args = parser.parse_args()

    summarize_benchmarks(args.input, args.output.joinpath(args.input.name + "_summary.csv"))
