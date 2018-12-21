# generates a script for executing more 
# tests using the parameters in "newparams"

#!/bin/bash


rm -f allexps.sh
for inst in ../../instances/mip/*.mps.gz;
do
	while read line
	do
		echo "./runcbcroot.sh $inst $line" >> allexps.sh
	done < newparams    
done

cat allexps.sh | sort -R > expsprndord.sh
rm allexps.sh

echo "call:"
echo "\trm -f nohup ; nohup parallel -j 7 :::: ./expsprndord.sh  &"
echo "to execute new experiments in parallel"
