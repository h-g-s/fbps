#!/bin/bash
###############################################################################
# This script is to tune the CLP solver software.
#
# PARAMETERS:
# $1 is the ID of the candidate to be evaluated
# $2 is the instance ID
# $3 is the seed
# $4 is the instance name
# The rest ($* after `shift 4') are parameters 
#
# RETURN VALUE:
# This script should print a single numerical value (the value to be minimized).
###############################################################################

expFolder=~/git/fbps/data/experiments/cbc/irace
cd $expFolder
EXE=${expFolder}/runcbcrootirace.sh

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

#echo will run  $EXE $INSTANCE -randomSeed ${SEED} ${CONFIG_PARAMS} primals

startTime=$SECONDS
$EXE $INSTANCE -randomSeed ${SEED} ${CONFIG_PARAMS} primals 1> $STDOUT 2> $STDERR
totalTime=$(($SECONDS - $startTime + 1))

# The output of the candidate $CONFIG_ID should be written in the file 
# c${CONFIG_ID}.stdout 
# Does this file exist?
if [ ! -s "${STDOUT}" ]; then
    # In this case, the file does not exist. Let's exit with a value 
    # different from 0. In this case irace will stop with an error.
    error "${STDOUT}: No such file or directory"
fi

# Ok, the file exist. It contains the whole output 
# This script should return a single numerical value, the best objective 
# value found by this run. The following line is to extract
# this value from the file containing the output.

#echo FILE:
#cat ${STDOUT}
COST=$(cat ${STDOUT} | grep -o -E 'Best [-+0-9.e]+' | cut -d ' ' -f2)
if ! [[ "$COST" =~ ^[-+0-9.e]+$ ]] ; then
    error "${STDOUT}: Output is not a number"
fi

if (( $(echo "$COST < 3000" |bc -l) )); then
  totalTime=$COST
fi

echo "$COST" "$totalTime"

# We are done with our duty. Clean files and exit with 0 (no error).
rm -f "${STDOUT}"
if [ ! -s ${STDERR} ]; then
    rm -f ${STDERR}
fi
rm -f best.* stat.* cmp.*
exit 0
