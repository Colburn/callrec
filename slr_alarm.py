#!/usr/bin/python  
#===============================================================================
#
#          FILE:  slr_alarm.py
# 
#         USAGE:  python ./slr_alarm.py 
# 
#   DESCRIPTION:  Parses the SLR log to see if the Spanless Recorder service 
#                 is responding to SIP invites. If it is not, it is reloaded. 
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


import time
import subprocess 

slr_log_file='/root/scripts/slr_1.log'
slr_list = ''

slr_sleep_log='/opt/callrec/logs/sleeplog.log'
sleep_log = open(slr_sleep_log, 'a')
sleep_log.close()
create=''
sip=''


def readLog():
  global slr_list, slr_log_file
  slr_log = open(slr_log_file, 'r')
  slr_list = list(slr_log)
  slr_log.close()


def getPID():
  global SLR, slrpid, slrerr
  SLR = subprocess.Popen(['/sbin/pidof', 'slr'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
  slrpid, slrerr = SLR.communicate()

def findCreate():
  global create, slr_sleep_log, slr_list
  readLog()
  getPID()
  for i in slr_list[-200:-1]:
    if 'CREATE' in i:
      create = 1
      break
    else:
      create = 0


def findSipApp():
  readLog()
  global sip, slr_list
  for i in slr_list[-200:-1]:
    if 'sip.app' in i:
      sip = 1
      break
    else: 
      sip = 0
      continue


def writeLog(x):
  global slr_sleep_log, sleep_log
  sleep_log = open(slr_sleep_log, 'a')
  sleep_log.write(time.ctime(time.time()) + x)
  sleep_log.close()

def restart():
  restartSlr=subprocess.call(['/opt/callrec/bin/rc.callrec_slr', 'restart'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  getPID()
  writeLog(' INFO: slr restarted due to silence. Exiting... pid=' + slrpid)
  quit()

def checkMsgs():
  global sleep_log, sip, create
  findCreate()
  findSipApp()
  counter=0
  while counter < 3:
    if sip==1 and create==1:
      getPID()
      writeLog(' INFO: slr is running fine. Exiting... pid=' + slrpid)
      quit()
    elif sip==0 and create==1:
      time.sleep(5)
      writeLog(' INFO: no sip packets found, trying again... pid=' + slrpid) 
      findSipApp()
      counter +=1
    else:
      writeLog(' INFO: No create messages found. Exiting.... pid=' + slrpid)      
      quit()
  getPID()
  writeLog(' ERROR: slr is silent. Will be restarted. pid=' + slrpid)
  restart() 	 

checkMsgs()

