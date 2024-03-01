#!/bin/bash
set -eu

if [[ "$PWD" != *"/experiments/memory_footprint/"* ]]; then
	# mosmodel expects mosalloc to gather information into a file duing memory footprint phase
	# so only use the allocator when not in that phase
	export $(< env.sh)
fi

if [[ "${USE_THP:-0}" == "1" ]]; then
	sudo bash -c "echo always > /sys/kernel/mm/transparent_hugepage/enabled
	echo always > /sys/kernel/mm/transparent_hugepage/defrag
	echo 1 > /sys/kernel/mm/transparent_hugepage/khugepaged/defrag
	if [[ -e /sys/kernel/mm/transparent_hugepage/ingens ]]; then
		echo 0 > /sys/kernel/mm/transparent_hugepage/ingens/deferred_mode
		echo 0 > /sys/kernel/mm/transparent_hugepage/ingens/util_threshold
		echo 0 > /sys/kernel/mm/transparent_hugepage/ingens/compact_sleep_millisecs
	fi"
fi

if [[ "${USE_INGENS:-0}" == "1" ]]; then
	sudo bash -c "echo always > /sys/kernel/mm/transparent_hugepage/enabled
	echo always > /sys/kernel/mm/transparent_hugepage/defrag
	echo 1 > /sys/kernel/mm/transparent_hugepage/khugepaged/defrag
	if [[ -e /sys/kernel/mm/transparent_hugepage/ingens ]]; then
		echo 1 > /sys/kernel/mm/transparent_hugepage/ingens/deferred_mode
		echo 90 > /sys/kernel/mm/transparent_hugepage/ingens/util_threshold
		echo 0 > /sys/kernel/mm/transparent_hugepage/ingens/compact_sleep_millisecs
	fi"
fi

source real_run.sh

if [[ "${USE_THP:-0}" == "1" || "${USE_INGENS:-0}" == "1" ]]; then
	echo "never" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
fi
