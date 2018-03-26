#!/usr/bin/python
#===============================================================================
#
#          FILE:  callfromlog.py
# 
#         USAGE:  python ./callfromlog.py
# 
#   DESCRIPTION: Will  read through core.log and restore database records
#                 from data that is in the log.                   
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  Install PyYaml on machine
#        AUTHOR: Colburn Hayden (CH), colburn.hayden@zoomint.com
#       COMPANY: Zoom International, Franklin, TN
#       CREATED: 2018-01-08
#      REVISION:  ---
#===============================================================================


#install PyYaml on customer machine
import yaml
import time
import pg
from datetime import datetime
import re
import logging

logging.basicConfig(filename='callfromlog.log', level=logging.DEBUG)

year='2017'

inputLog='short.log'

#DB Variables
dbName='fromlogs'
dbUser='callrec'
dbPasswd='callrec'
dbHost='10.33.64.108'
dbPort=5432
callrec=pg.DB(dbName, dbHost, dbPort, None, None, dbUser, dbPasswd)


callHashArray=[]
groupCounter=0
currentCall=0

dateRegex=r'([A-Za-z]{0,4})\s([0-9]{1,2})\s([0-9]{2}):([0-9]{2}):([0-9]{2})'


#Take log date format and convert it to PostgreSQL date format
def parseDate(date):
	timeStruct=time.strptime(date, "%b %d %H:%M:%S %Y")
	return time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)

def epochDate(date):
	timeStruct=time.strptime(date, "%b %d %H:%M:%S %Y")
	return time.mktime(timeStruct)

def getCoupleLength(start, stop):
	startStruct=time.strptime(start, "%Y-%m-%d %H:%M:%S")
	stopStruct=time.strptime(stop, "%Y-%m-%d %H:%M:%S")
	length=time.mktime(stopStruct)-time.mktime(startStruct)
	return int(length)


#take cfile data from log and convert to python object
#using yaml library
def convertCfileDataToYaml(logData):
	logData=logData.replace('=', ' : ')
	newLogData=re.sub(r'([A-Za-z]+){', '{', logData)
	yamlData=yaml.load(newLogData)
	return yamlData


#read the logfile line by line, calling functions for each log event parsed
def readLogFile():
	with open(inputLog, 'r') as coreLogFile:
		coreLogLines=coreLogFile.readlines()
		for line in coreLogLines:
			if re.search(r'call created[.]', line):
				createCall(line)
			elif re.search(r'call removed[.]', line):
				finishCall(line)
			elif re.search(r'couple created[.]', line):
				createCouple(line)
			elif re.search(r'couple removed[.]', line):
				finishCouple(line)
			elif re.search(r'COUPLE.*saved to db', line):
				idDbMatcher(line)
			elif re.search(r'Processing[:] DecodingResponse', line):
				createCfile(line)
		saveCalls(callHash)


#save data to the DB
def saveCalls(callHash):
	for callHash in callHashArray:
		for callid in callHash:
			call=callHash[callid]	
			callSaved=call.save()
			if callSaved != False:
				logging.debug("saved call: {0}".format(call.callid))
				for coupleid in call.couples:
					couple=call.couples[coupleid]
					for item in [couple.callid, couple.start_ts, couple.stop_ts, couple.length, couple.callingnr, couple.originalcallednr]:
						logging.debug("logging couple item {0}".format(item))
					coupleSaved=couple.save()
					if coupleSaved != False:
						logging.debug("saved couple: {0}".format(couple.coupleid))
						for cfileid in couple.cfiles:
							cfile=couple.cfiles[cfileid]
							cfileSaved=cfile.save()
							logging.debug("saved cfile: {0}".format(cfile.cfileid))

def getID(dataString):
	return re.search(r'([0-9])+', dataString).group(0)


#create a Call instance with initial data
def createCall(line):
	callidString=getID(re.search(r'Call:([0-9])+', line).group(0))

	if currentCall==0:
		currentCall=int(callidString)
		
	if int(callIdString)<currentCall:
		groupCounter+=1
		callHashArray[groupCounter]={}

	call=callHashArray[groupCounter][callidString]=Call(int(callidString))
	dateString=re.search(dateRegex, line).group(0)
	call.start_ts=parseDate("{0} {1}".format(dateString, year))



#finish call instance and add stop ts and cplcnt
def finishCall(line):
	callidString=getID(re.search(r'Call:([0-9])+', line).group(0))
	try:
		call=callHashArray[groupCounter][callidString]
		dateString=re.search(dateRegex, line).group(0)

		call.stop_ts=parseDate("{0} {1}".format(dateString, year))
		call.cplcnt=len(call.couples)
	except KeyError: 
		logging.warning("Key errror while finishing call")

#create couple instance with initial data

def createCouple(line):
	coupleidString=getID(re.search(r'Couple:([0-9])+', line).group(0))
	logging.warning('Found couple {0}'.format(coupleidString))
	callidString=getID(re.search(r'Call:([0-9])+', line).group(0))
	try:
		couple=callHash[groupCounter][callidString].couples[coupleidString]=Couple(int(coupleidString))
		couple.callid=int(callidString)
	
		dateString=re.search(dateRegex, line).group(0)
		couple.start_ts=parseDate("{0} {1}".format(dateString, year))
 
		couple.callingnr=re.search(r'callingNumber[=](([A-Za-z0-9+])+)', line).group(0).replace('callingNumber=', '')
		couple.originalcallednr=re.search(r'calledNumber[=](([A-Za-z0-9+])+)', line).group(0).replace('calledNumber=', '')
		couple.sid="{0}_{1}_{2}_{3}".format(epochDate("{0} {1}".format(dateString, year)), couple.coupleid, couple.callingnr, couple.originalcallednr)	
	except KeyError as keyErr:
		logging.warning("Error creating couple due to key error")
		logging.warning(keyErr)



#finish couple and add stop_ts
def finishCouple(line):
	callidString=getID(re.search(r'Call:([0-9])+', line).group(0))
	coupleidString=getID(re.search(r'Couple:([0-9])+', line).group(0))
	try:
		couple=callHashArray[groupCounter][callidString].couples[coupleidString]
		dateString=re.search(dateRegex, line).group(0)
		couple.stop_ts=parseDate("{0} {1}".format(dateString, year))
		couple.length=getCoupleLength(couple.start_ts, couple.stop_ts)
	except KeyError as keyErr:
		logging.warning("Error finishing couple due to key error")
		logging.warning(keyErr)
		pass

#create cfile with all data
def createCfile(line):
	cfileDataString=re.search(r'(DecodingResponse{).*', line).group(0)
	cfileObj=convertCfileDataToYaml(cfileDataString.replace('DecodingResponse', ''))
	requestId=cfileObj['requestId']
	try:
		for callid in callHashArray[groupCounter]:
			for coupleid in callHashArray[groupCounter][callid].couples:
				couple=callHashArray[groupCounter][callid].couples[coupleid]
				if couple.idDb==requestId:
					cfile=couple.cfiles[requestId]=Cfile(requestId) 
					cfile.cplid=couple.coupleid
					cfile.cftype=cfileObj['type']
					media=cfileObj['decodedMedia']
				#	if cfile.cftype=='AUDIO':
				#	couple.length=media['length']
					cfile.cfpath=media['mediaPath']
					cfile.enc_key_id=media['encryptionKeyId']
					cfile.digest=media['digest']
					cfile.ckvalue=media['checksum']
					cfile.cktype=media['checksumType']
					cfile.start_ts=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(media['startTime']/1000))
					cfile.stop_ts=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(media['stopTime']/1000))
					#cfile.sgid=callrec.query('select callrec.GET_NEXT_SGRPID()').getresult()[0][0]
					break
					
	except KeyError as keyErr:
		pass
		logging.warning("Key Error when creating cfile")
		logging.warning(keyErr) 


#While most log lines identify the Call: and Couple: ids
#the decoding details do not. Instead they have a requestId which
#will match the idDB. When couple is saved to DB, both the Couple details and idDB
#are present and can be leveraged to match couples to cfiles

def idDbMatcher(line):
	coupleidString=getID(re.search(r'Couple:([0-9])+', line).group(0))
	callidString=getID(re.search(r'Call:([0-9])+', line).group(0))
	try:
		couple=callHashArray[groupCounter][callidString].couples[coupleidString]
		couple.idDb=int(getID(re.search(r'idDb\s[=]\s([0-9]+)', line).group(0)))
	except KeyError:
		pass

#Call class
class Call(object):
		
	def __init__(self, callid):
		self.callid=callid
		self.start_ts=''
		self.stop_ts=''
		self.length=''
		self.cplcnt=''
		self.couples={}

	def save(self):
		if all(column!='' for column in [self.start_ts, self.stop_ts, self.cplcnt]):
			self.callid=int(callrec.query("select add_call('{0}')".format(self.cplcnt)).dictresult()[0]['add_call'])
			callrec.query("update calls set start_ts='{0}', stop_ts='{1}' where id={2}".format(self.start_ts, self.stop_ts, self.callid))
			for coupleid in self.couples:
				self.couples[coupleid].callid=self.callid
			return True
		else:
			return False


#Couple class
class Couple(object):
	def __init__(self, coupleid):
		self.coupleid=coupleid
		self.callid=''
		self.start_ts=''
		self.stop_ts=''
		self.length=''
		self.callingnr=''
		self.originalcallednr=''
		self.cfiles={}
		self.idDb=''

	def save(self):
		if all(column!= '' for column in [self.callid, self.start_ts, self.stop_ts, self.length, self.callingnr, self.originalcallednr]):
			self.coupleid=int(callrec.query("select add_couple({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}')".format(self.callid, self.start_ts, self.stop_ts, "0.0.0.0", "0.0.0.0", self.callingnr, self.originalcallednr, self.originalcallednr, 'UNKNOWN', 'UNKNOWN', 'NORMAL', 'NO_PROBLEM', self.sid, '', len(self.cfiles), 'f')).dictresult()[0]['add_couple'])
			callrec.query("update couples set length='{0}' where id={1}".format(self.length, self.coupleid))
			for cfileid in self.cfiles:
				self.cfiles[cfileid].cplid=self.coupleid
			callrec.query("insert into couple_extdata (key, value, cplid) values ('Note', 'Restored from log', {0})".format(self.coupleid))
			
			return True
		else:
			return False

#Cfile class
class Cfile(object):
	def __init__(self, cfileid):
		self.cfileid=cfileid
		self.cplid=''
		self.cftype=''
		self.cfpath=''
		self.enc_key_id=''
		self.digest=''
		self.start_ts=''
		self.stop_ts=''
		self.ckvalue=''
		self.cktype=''
		self.sgid=''

	def save(self):
		if all(column!='' for column in [self.cplid, self.cftype, self.cfpath, self.enc_key_id, self.digest, self.start_ts, self.stop_ts, self.ckvalue, self.cktype, self.sgid]):
			self.cfileid=int(callrec.query("select add_cfile({0}, '{1}', '{2}', '{3}', '{4}', '{5}')".format(self.cplid, '0', self.cktype, self.ckvalue, self.cftype, self.cfpath)).dictresult()[0]['add_cfile'])
			callrec.query("update cfiles set enc_key_id='{0}', digest='{1}', start_ts='{2}', stop_ts='{3}' where id={4}".format(self.enc_key_id, self.digest, self.start_ts, self.stop_ts, self.cfileid))
			return True
		else:
			return False

readLogFile()
callrec.close()
