#!/bin/bash
set -eu

if [[ "$PWD" != *"/experiments/memory_footprint/"* ]]; then
	# mosmodel expects mosalloc to gather information into a file duing memory footprint phase
	# so only use the allocator when not in that phase
	export $(< env.sh)
fi

if [[ "${USE_THP:-0}" == "1" ]]; then
	echo "always" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
fi

source real_run.sh

if [[ "${USE_THP:-0}" == "1" ]]; then
	echo "never" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
fi
