#! /bin/bash

if (( $# < 1 )); then
    echo "Usage: $0 \"command_to_execute\""
    exit -1
fi

command="$@"

MEASURE_HUGE_PID=0

function cleanup {
        if [[ "${MEASURE_HUGE_PID:-0}" != "0" ]]; then
                kill -s SIGINT $MEASURE_HUGE_PID
        fi
}

general_events="ref-cycles,instructions,page-faults,cache-misses,cache-references,"

# We no longer measure the cache events because we want to reduce sampling and improve the measuring accuracy.
#general_events+=",L1-dcache-loads,L1-dcache-stores,L1-dcache-load-misses,L1-dcache-store-misses"
#general_events+=",LLC-loads,LLC-stores,LLC-load-misses,LLC-store-misses"

prefix_perf_command="perf stat --field-separator=, --output=perf.out"
# extract architecture specific dtlb and energy events from 'ocperf list' output
#dtlb_events=`perf list | \grep -o "dtlb_.*_misses\.\w*" | sort -u | tr '\n' ','`
#dtlb_events=${dtlb_events%?} # remove the trailing , charachter
#dtlb_events=dtlb_load_misses.miss_causes_a_walk,dtlb_load_misses.walk_duration,dtlb_store_misses.miss_causes_a_walk,dtlb_store_misses.walk_duration

dtlb_events=dtlb_load_misses.miss_causes_a_walk:P,dtlb_store_misses.miss_causes_a_walk:P

perf_command="$prefix_perf_command --event $general_events$dtlb_events -- "

time_format="seconds-elapsed,%e\nuser-time-seconds,%U\n"
time_format+="kernel-time-seconds,%S\nmax-resident-memory-kb,%M"
time_command="time --format=$time_format --output=time.out"

submit_command="$perf_command $time_command"
echo "Running the following command:"
echo "$submit_command $command"

trap cleanup EXIT
$(dirname $BASH_SOURCE)/measure_huge_usage.py &
MEASURE_HUGE_PID=$!
$submit_command $command
