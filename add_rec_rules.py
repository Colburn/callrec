#!/usr/bin/python  
#===============================================================================
#
#          FILE:  add_rec_rules.py
# 
#         USAGE:  python ./add_rec_rules.py
# 
#   DESCRIPTION: Adds mass list of extensions to recording rules. All rec_rules
#                 are added with like configuration.                  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Colburn Hayden (CH), colburn.hayden@zoomint.com
#       COMPANY: Zoom International, Prague
#       CREATED: 2016-12-14
#      REVISION:  ---
#===============================================================================



import pg

#variable assignments.

userid=1
roleid=1
isactive='t'
weekdays=1111111
starttime=0
stoptime=86400
numbermask='>{0}???????' #mask of recording rules.
probability=100
policy='NO_RECORD'
factory='PHONE'

screenrec='false' #does rule apply to screens?
scr_prob=100

#Define list of areacodes
areacodefile='./areacodes.txt'

#Rec Rules insert command
add_rules="insert into rec_rules (id, userid, roleid, isactive, weekdays, starttime, stoptime, numbermask, priority, probability, policy, factory) values (nextval('seq_rec_rules'), {0}, {1}, '{2}', '{3}', '{4}', '{5}', '{6}', {7}, '{8}', '{9}', '{10}') returning id;"

add_rules_process="insert into rec_rules_process (ruleid, type, value) values ({0}, 'INTERNAL_DATA_MODIFICATOR', '{1} = {2}');"

#connect to DB
callrec = pg.DB('callrec', 'localhost', 5432, None, None, 'callrec', 'callrec')

#Read the defined list of exentions separated by newline characters
ac=list(open(areacodefile).read().split('\n'))
areacodes=ac[:len(ac)-1]

#Find highest rec rules priority
#lower priority of existing rec_rules
priority=callrec.query("select * from rec_rules order by priority desc limit 1;").dictresult()
if len(priority) == 1:
  priority=priority[0]['priority']
  callrec.query("update rec_rules set priority=priority-{0}".format(len(areacodes)))
else:
  priority=999

#iterate over extensions and insert them into the DB
for code in areacodes:
  new_id=callrec.query(add_rules.format(userid, roleid, isactive, weekdays, starttime, stoptime, numbermask.format(code), priority, probability, policy, factory)).dictresult()
  priority=priority-1
  if screenrec == 'true':
    callrec.query(add_rules_process.format(new_id[0]['id'], 'SRS_RECORD_FLAG', 'true'))
    callrec.query(add_rules_process.format(new_id[0]['id'], 'SRS_RECORD_PROBABILITY', scr_prob))
