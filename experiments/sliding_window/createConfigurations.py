#!/usr/bin/env python3

kb = 1024
mb = 1024*kb
gb = 1024*mb

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--memory_footprints', default='memory_footprints.txt')
parser.add_argument('-r', '--hot_region', default='hot_region.txt')
parser.add_argument('-b', '--benchmark', required=True)
parser.add_argument('-n', '--num_configurations', type=int, default=9)
parser.add_argument('-t', '--weight', type=int, default=50)
parser.add_argument('-g', '--use_1gb_pages', action='store_true')
parser.add_argument('-o', '--output', required=True)
args = parser.parse_args()

standard_page_size = 4*kb
window_page_size = 2*mb
if args.use_1gb_pages:
    window_page_size = 1*gb

import math
def round_up(x, base):
    return int(base * math.ceil(x/base))

def round_down(x, base):
    return (int(x / base) * base)


def isPowerOfTwo(number):
    return (number != 0) and ((number & (number - 1)) == 0)

num_configurations = args.num_configurations - 1
if not isPowerOfTwo(num_configurations):
    raise ValueError('Number of configurations is not power of two')

import sys
import pandas as pd
footprints_df = pd.read_csv(args.memory_footprints, index_col='benchmark')

hot_region_df = pd.read_csv(args.hot_region, index_col=False, comment='#')
conf_row = hot_region_df[hot_region_df['window-weight'] == args.weight]
hot_region_start_page = conf_row['window-start'].iloc[0]
hot_region_num_pages = conf_row['window-length'].iloc[0]
if hot_region_start_page < 0 or hot_region_num_pages < 0:
    sys.exit('benchmark [' + args.benchmark + '] has no ' + str(args.weight) + '% weighted window')
hot_region_start =  hot_region_start_page * standard_page_size
hot_region_length = hot_region_num_pages * standard_page_size

mmap_footprint = footprints_df.loc[args.benchmark]['anon-mmap-max']
brk_footprint = footprints_df.loc[args.benchmark]['brk-max']

hot_region_brk_start = conf_row['brk-start'].iloc[0]
hot_region_brk_size = conf_row['brk-length'].iloc[0]
brk_ratio = brk_footprint / hot_region_brk_size
window_start = round_down((int(hot_region_start * brk_ratio)), standard_page_size)
raw_window_length = round_up(int(hot_region_length * brk_ratio), standard_page_size)
window_length = round_up(raw_window_length, window_page_size)

window_end = window_start + window_length

# extend pool footprint in case the window exceeds it (due to rounding works)
brk_footprint = max(brk_footprint, window_end)

# check where to move the window: to left or right (to the direction with enough space)
if window_start > window_length:
    start_offset = window_start - window_length
elif (window_length + window_end) <= brk_footprint:
    start_offset = window_start
else:
    start_offset = window_start
    brk_footprint = window_end + window_length

window_overcommit_max_size = 5 * standard_page_size
if (start_offset + 2*window_length) > brk_footprint and \
    (start_offset + 2*window_length) <= (brk_footprint + window_overcommit_max_size):
        brk_footprint = (start_offset + 2*window_length)

if (start_offset + 2*window_length) > brk_footprint:
    sys.exit(str.format('window <{0} : {1}> of benchmark <{2}> exceeds the benchmark memory footprint <{3}>',
        start_offset, (start_offset + 2*window_length), args.benchmark, brk_footprint))

conf_prefix = str.format('-fps 1GB -aps {0} -bps {1}',
        mmap_footprint, brk_footprint)

step_size = math.floor(raw_window_length / (args.num_configurations-1))
step_size = round_up(step_size, 4*kb)

configurations = ''
conf_line_format = '{0} -bs2 {1} -be2 {2} -bs1 {3} -be1 {4}\n'
if args.use_1gb_pages:
    conf_line_format = '{0} -bs1 {1} -be1 {2} -bs2 {3} -be2 {4}\n'
for i in range(0, args.num_configurations):
    config = str.format(conf_line_format,
            conf_prefix,
            start_offset, (start_offset + window_length),
            0, 0)
    configurations += config
    start_offset += step_size

with open(args.output, 'w') as output_fid:
    print(configurations, file=output_fid)



