#!/bin/bash
###############################################################################
# This script is to tune the ACOTSP software.
#
# PARAMETERS:
# $1 is the ID of the candidate to be evaluated
# $2 is the instance ID
# $3 is the seed
# $4 is the instance name
# The rest ($* after `shift 4') are parameters for running ACOTSP
#
# RETURN VALUE:
# This script should print a single numerical value (the value to be minimized).
###############################################################################

# Path to the ACOTSP software:
chmod +x /home/haroldo/matheus/tuning/runcbcrootirace.sh
EXE=/home/haroldo/matheus/tuning/./runcbcrootirace.sh

# Fixed parameters that should be always passed to ACOTSP.
# The time to be used is always 5 seconds, and we want only one run:

CONFIG_ID="$1"
INSTANCE_ID="$2"
SEED="$3"
INSTANCE="$4"
# All other parameters are the candidate parameters to be passed to program
shift 4 || error "Not enough parameters to $0"
CONFIG_PARAMS=$*

STDOUT=c${CONFIG_ID}-${INSTANCE_ID}.stdout
STDERR=c${CONFIG_ID}-${INSTANCE_ID}.stderr

# In case of error, we print the current time:
error() {
    echo "`TZ=UTC date`: error: $@" >&2
    exit 1
}

if [ ! -x "${EXE}" ]; then
    error "${EXE}: not found or not executable (pwd: $(pwd))"
fi

# Now we can call ACOTSP by building a command line with all parameters for it
#ulimit -t 72
$EXE $INSTANCE ${CONFIG_PARAMS} duals solve 1> $STDOUT 2> $STDERR
#EXE $INSTANCE ${FIXED_PARAMS} ${CONFIG_PARAMS} solve > $STTESTE
#$EXE1 1> $STDOUT 2> $STDERR

# The output of the candidate $CONFIG_ID should be written in the file 
# c${CONFIG_ID}.stdout (see target runner for ACOTSP).
# Does this file exist?
if [ ! -s "${STDOUT}" ]; then
    # In this case, the file does not exist. Let's exit with a value 
    # different from 0. In this case irace will stop with an error.
    error "${STDOUT}: No such file or directory"
fi

# Ok, the file exist. It contains the whole output written by ACOTSP.
# This script should return a single numerical value, the best objective 
# value found by this run of ACOTSP. The following line is to extract
# this value from the file containing ACOTSP output.
#COST=$(cat ${STDOUT} | grep -o -E 'Best [-+0-9.e]+' | cut -d ' ' -f2)
#if ! [[ "$COST" =~ ^[-+0-9.e]+$ ]] ; then
#    error "${STDOUT}: Output is not a number"
#fi
COST=$(tail -1 ${STDOUT})
# Print it!
echo "$COST"

# We are done with our duty. Clean files and exit with 0 (no error).
#rm -f "${STDOUT}" "${STDERR}"
rm -f best.* stat.* cmp.*
exit 0
