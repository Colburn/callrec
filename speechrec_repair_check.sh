
updatedb

#Uncomment notlike if you want to avoid changing the name to oldext files with 'sox' in the filename
#notlike=and\ cfpath\ not\ like\ \'%sox%\'
callsdir=/opt/callrec/data/calls
oldext=wav
newext=_sox\.mp3
dbname=callrec
count=`psql -U postgres $dbname -c "select count(*) from cfiles where cfpath like '%$oldext%' $notlike;" | awk {'print $1'} | grep [0-9] | grep -v '('`



function check_file {
	finder=`locate $1`
	if [[ $finder != "" ]]; then
		psql -U postgres $dbname -c "update cfiles set cfpath='$1' where cfpath='$i';"
	else 
		prefix=`echo $i | sed -e 's/_sox//g' | sed -e 's/\.[a-z]\{1,3\}//g'`
		truefile=`locate $prefix`
		if [[ $truefile != "" ]]; then
			psql -U postgres $dbname -c "update cfiles set cfpath='$truefile' where cfpath='$i';"
		else
			now=`date +'%D %T'`
			echo "$now Attempted to update $i to $1, but target file does not exist on the file system. Skipping file..." >> /opt/callrec/logs/SpeechREC_repair.log
		fi
	fi
}


if [ $count  -gt 0 ]; then
        while [[ $count = ^-?[0-9]+$  ]] || [[ $count -gt 0 ]]; do
                x=`psql -U postgres $dbname -c "select cfpath from cfiles where cfpath like '%$oldext%' $notlike limit 100;" | grep $callsdir`
                for i in $x; do
                        z=`echo $i | sed -e "s/$oldext/$newext/g"`
                        check_file $z
                done;
                count=`expr $count-100`
        done
fi
