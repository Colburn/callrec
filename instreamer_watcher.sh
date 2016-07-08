#!/bin/bash - 
#===============================================================================
#
#          FILE:  instreamer_watcher.sh
# 
#         USAGE:  ./instreamer_watcher.sh <start|stop|restart|oneshot>
# 
#   DESCRIPTION:  Runs as a daemon to watch an active instreamer connection (ip_addr) 
# 				  and restarts instreamer service if no connection present
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Colburn Hayden (CH), colburn.hayden@zoomint.com
#       COMPANY: Zoom International, Prague
#       CREATED: 07.08.2016 14:30:00 CET
#      REVISION:  ---
#===============================================================================

date=`date`
PIDFILE=/opt/callrec/run/instreamer_watcher.pid
logfile=/opt/callrec/logs/instreamer_watcher.log

email_addr=colburn.hayden@zoomint.com
ip_addr=`cat /opt/callrec/etc/extras.xml | grep '"streamUrl"' | sed -e 's/.*<Value name="streamUrl">//g' -e 's/<\/Value>//g'
connection=`netstat -tupn | grep $ip_addr`
check_connection() {
        if [[ $connection = '' ]]; then
                /opt/callrec/bin/rc.callrec_instreamer restart > /dev/null &2>1
                echo "$date Instreamer at address $i went down: restarting " >> $logfile
                #echo "$date Instreamer went down: restarting" | mail -s "Instreamer alert" $email_addr

        else
                echo "$date Instreamer is running fine on pid" `cat $PIDFILE` >> $logfile
        fi
}


startDaemon() {
        touch $PIDFILE
        echo $BASHPID > $PIDFILE
        while true; do
				for i in ip_addr; do
					connection=`netstat -tupn | grep $i`
					date=`date`
					echo "$date Checking the process" >> $logfile
					check_connection
					wait
				done
				sleep 5s
        done
}
stopDaemon() {
        if [ -f $PIDFILE ]; then
                echo "$date Stopping Daemon" >> $logfile
                kill -9 `cat $PIDFILE`
                rm -f $PIDFILE
                echo "$date Stopped the watcher script" >> $logfile
                exit 0
        else
                echo "$date There is not watcher process to stop"
        fi
}

restartDaemon() {
	stopDaemon
	startDaemon

}

oneshot() {
	for i in ip_addr; do
		connection=`netstat -tupn | grep $i`
		date=`date`
		echo "$date Checking the process" >> $logfile
		check_connection
		wait
	done
}

case "$1" in
	start)
		if [ -f $PIDFILE ]; then
			echo "$date Instreamer watcher daemon is already running at PID:" `cat $PIDFILE` >> $logfile
			exit 0
		else
			startDaemon &
		fi
		;;
	stop)
		stopDaemon
		;;
	oneshot)
		oneshot
		;;
		*)
	echo "Error: usage $0 {start | stop | restart | oneshot}"
esac
exit 0
