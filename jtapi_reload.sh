#!/bin/bash - 
#===============================================================================
#
#          FILE:  jtapi_reload.sh
# 
#         USAGE:  ./jtapi_reload.sh 
# 
#   DESCRIPTION:  Switches primary provider entry in sniffers.xml and reloads 
#                 JTAPI service. Workaournd for CUCM 8.6 bug where devices 
#		  are improperly reported 'Out of Service.'
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Colburn Hayden (CH), colburn.hayden@zoomint.com
#       COMPANY: Zoom International, Prague
#       CREATED: 05.02.2016 13:00:00 CET
#      REVISION:  ---
#===============================================================================

callrec_etc=/opt/callrec/etc
callrec_bin=/opt/callrec/bin
ip_address_new=''

ip_address=`cat $callrec_etc/sniffers.xml | grep '"name"' | sed -e 's/.*<Value name="name">//g' -e 's/<\/Value>//g'`
ip_address="${ip_address//"."/\\.}"

IFS=,
count=`echo $ip_address| wc -w`

if [ $count -ge 2 ]; then
        for i in $ip_address; do
                if [[ $ip_address_new = '' ]]; then
                        ip_address_new=$i
                else
                        ip_address_new=$i,$ip_address_new
                fi
        done
        unset IFS
        sed -i -e "s/$ip_address/$ip_address_new/g" $callrec_etc/sniffers.xml
fi

$callrec_bin/rc.callrec_configmanager reload
$callrec_bin/rc.callrec_rts_jtapi restart
