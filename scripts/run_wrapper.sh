#!/bin/bash
set -eu

if [[ "$PWD" != *"/experiments/memory_footprint/"* ]]; then
	# mosmodel expects mosalloc to gather information into a file duing memory footprint phase
	# so only use the allocator when not in that phase
	export $(< env.sh)
fi

source real_run.sh
