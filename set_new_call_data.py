#!/user/bin/python

import pg
import os
import datetime
import pwd

sep = os.path.sep
db='colerec'
callrec = pg.connect(db, 'localhost', 5432, None, None, 'callrec', 'callrec')
query='''
update {0} set start_ts=date_trunc('day', now())::date + 
		extract(hour from start_ts) * interval '1 HOUR' + 
		extract(minute from start_ts) * interval '1 MINUTE' + 
		extract(second from start_ts) * interval '1 SECOND',
stop_ts=date_trunc('day', now())::date + 
		extract(hour from start_ts) * interval '1 HOUR' + 
		extract(minute from start_ts) * interval '1 MINUTE' + 
		extract(second from start_ts) * interval '1 SECOND'
'''
qualifier=" where description='UCCE'"
filesQuery="select cfpath from cfiles where cplid in (select id from couples {0})".format(qualifier)
tables=['couples', 'cfiles', 'calls']

uid=pwd.getpwnam('callrec')[2]
gid= pwd.getpwnam('callrec')[3]



def moveFiles():
	files=callrec.query(filesQuery).getresult()
	for file in files:
		callsDir=datetime.datetime.now().strftime('%Y%m%d')
		parent=os.path.abspath(os.path.dirname(file[0]) + sep + '..')
		fullCallsDir=parent+sep+callsDir
		if os.path.exists(fullCallsDir) == False:
			os.mkdir(fullCallsDir)
			os.chown(fullCallsDir, uid, gid)
		if os.path.exists(file[0]):
			os.rename(file[0], fullCallsDir+sep+os.path.basename(file[0]))
			callrec.query("update cfiles set cfpath=replace('{0}', '{1}', '{2}') where cfpath='{0}'".format(file[0], os.path.basename(os.path.dirname(file[0])), callsDir))



def updateDate():
	for i in tables:
		if i == 'couples':
				add_query="{0}".format(qualifier)
		elif i == 'calls':
			add_query=" where id in (select callid from couples {0})".format(qualifier)
		elif i == 'cfiles':
			add_query=" where cplid in (select id from couples {0})".format(qualifier)

		callrec.query(query.format(i) + add_query)

updateDate()
moveFiles()
