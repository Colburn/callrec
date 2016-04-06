count=`psql -U postgres callrec -c "select count(*) from cfiles where cfpath like '%wav%';" | awk {'print $1'} | grep [0-9] | grep -v '('`

if [ $count  -gt 0 ]; then
        while [[ $count = ^-?[0-9]+$  ]] || [[ $count -gt 0 ]]; do
                x=`psql -U postgres callrec -c "select cfpath from cfiles where cfpath like '%wav%' limit 100;" | grep data`
                for i in $x; do
                        z=`echo $i | sed -e 's/wav/mp3/g'`
                        psql -U postgres callrec -c "update cfiles set cfpath='$z' where cfpath='$i';"
                done;
                count=`expr $count-100`
        done
fi

