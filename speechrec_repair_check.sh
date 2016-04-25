
#!/bin/bash - 
#===============================================================================
#
#          FILE:  speechrec_repair_check.sh
# 
#         USAGE:  ./speechrec_repair_check.sh 
# 
#   DESCRIPTION:  Edits cfiles table to contain the correct AUDIO file path where 
#                 SpeechREC did not properly update cfpath.
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Colburn Hayden (CH), colburn.hayden@zoomint.com
#       COMPANY: Zoom International, Prague
#       CREATED: 04.22.2016 14:30:00 CET
#      REVISION:  ---
#===============================================================================


updatedb
#Uncomment notlike if you want to avoid changing the name to oldext files with 'sox' in the filename
#notlike=and\ cfpath\ not\ like\ \'%sox%\'
callsdir=/opt/callrec/data/calls
oldext=\.wav
newext=_sox\.mp3
dbname=callrec
now=`date +'%D %T'`
count=`psql -U postgres $dbname -c "select count(*) from cfiles where cfpath like '%$oldext%' $notlike;" -A | grep "^[0-9]*$"`
echo "$now Found $count calls to repair" >> /opt/callrec/logs/SpeechREC_repair.log


function check_file {
        finder=`locate $1`
        if [[ $finder != "" ]]; then
                now=`date +'%D %T'`
                echo "$now  couple:[$couple]   Found $1 on file system. Changing $i to $1 in DB" >> /opt/callrec/logs/SpeechREC_repair.log
                psql -U postgres $dbname -c "update cfiles set cfpath='$1' where cfpath='$i';"
        else
                now=`date +'%D %T'`
                echo "$now  couple[$couple] Updated file $1 does not exist, truncating file extension locate proper call on filesystem." >> /opt/callrec/logs/SpeechREC_repair.log
                prefix=`echo $i | sed -e 's/_sox//g' | sed -e 's/\.[a-z]\{1,3\}//g'`
                truefile=`locate $prefix`
                if [[ $truefile != "" ]]; then
                        now=`date +'%D %T'`
                        echo "$now   couple[$couple] Found matching file on filesystem. Changing $i to $truefile in DB" >> /opt/callrec/logs/SpeechREC_repair.log
                        psql -U postgres $dbname -c "update cfiles set cfpath='$truefile' where cfpath='$i';"
                else
                        now=`date +'%D %T'`
                        echo "$now  couple[$couple] Attempted to update $i to $1, but target file does not exist on the file system. Skipping file..." >> /opt/callrec/logs/SpeechREC_repair.log
                fi
        fi
}


if [ $count  -gt 0 ]; then
        while [[ $count = ^-?[0-9]+$  ]] || [[ $count -gt 0 ]]; do
                x=`psql -U postgres $dbname -c "select cfpath from cfiles where cfpath like '%$oldext%' $notlike limit 100;" | grep /`
                for i in $x; do
                        couple=`psql -U postgres callrec -c "select cplid from cfiles where cfpath='$i';" -A | less | grep "^[0-9]*$"`
                        z=`echo $i | sed -e "s/$oldext/$newext/g"`
                        check_file $z
                done;
                count=`expr $count-100`
        done
fi
