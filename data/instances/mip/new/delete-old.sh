for file in *.mps.gz;
do
    iname=`basename $file .mps.gz`
    if [ -e ../${iname}.mps.gz ]
    then
        echo instance $iname exists, deleting
        rm $file
    else
        echo instance $iname is new
    fi
done
