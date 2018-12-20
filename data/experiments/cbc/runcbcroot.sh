# script to execute CBC solving the LP relaxation using 
# some parameter setting for CLP in a time limit (tl),
# check the output and store the result, i.e. the time 
# spent solving it
# if an error occurs or a solution with a wrong
# objective function is produced then the result
# is a penalty of 2*tm

export LC_NUMERIC="en_US.UTF-8"
iname=`basename $1 .mps.gz`
params="`echo \"${@:2}\" |  sed 's/[[:blank:]]/-/g'`"

timeLimit=4000
SECONDS=0

outfile="${iname}${params}.sol"
outfile=${outfile/--/-m}
errorfile="${iname}${params}.error"
errorfile=${outfile/--/-m}

if [ -s $outfile ]; 
then
    exit
fi

linesSumm=`cat relaxation.csv | grep -i "${iname},"  | grep -i ",${params}," | wc -l`

if [ ${linesSumm} -lt 1 ]
then
    echo solving instance $iname with parameters $params
else
    echo instance $iname already executed with params $params
    exit
fi


rm -f "$outfile"
echo will run timeout ${timeLimit}s cbc $1 keepnames off cuts off heur off passf 0 strong 0 trust 0 preprocess off strong 0 trust 0 maxn 0 ${@:2} solu ${outfile} > /dev/null 2> ${errorfile}

utime=`{ time -p timeout ${timeLimit}s cbc $1 keepnames off cuts off heur off passf 0 strong 0 trust 0 preprocess off strong 0 trust 0 maxn 0 ${@:2} solu ${outfile} > /dev/null 2> ${errorfile}; } 2>&1 >/dev/null | grep -i user | cut -d ' ' -f 2` 

#read -n1 kbd

fo=99999999
if [ -s $outfile ]; 
then
    
    if grep -q "Status unknown" "$outfile"; then
        fo=99999999
        utime=$(($timeLimit*2))
    else
        if grep -q "Stopped on iterations" "$outfile"; then
            fo=99999999
            utime=$(($timeLimit*2))
        else
            if grep -q "Infeasible -" "$outfile"; then
                fo=99999999
                utime=$(($timeLimit*2))
            else
                fo=`cat $outfile |  grep -i "objective value" | cut -d ' ' -f 13`
                #echo fo: $fo
                if [ ! "$fo" ]; 
                then
                    fo=`cat $outfile | grep -i "\- objective value" | cut -d ' ' -f 5`
                fi
            fi
        fi
    fi
   rm ${outfile}
else
    utime=$(($timeLimit*2))

    if [ "${SECONDS}" -lt "3500" ]; then
        echo $iname,${@:2} >> bugs.csv
    fi
fi

if [ -s ${errorfile} ];
then
    echo error on $iname with parameters ${@:2}
else
    rm -f ${errorfile}
fi

echo "${iname},${params},${utime},${fo}" >> relaxation.csv

