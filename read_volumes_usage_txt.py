#!/usr/bin/python


def validateNumLen(storageSpace):
	if len(str(storageSpace)) < 8:
		returnValue="{0}MB".format(float(storageSpace/1024))
	else:
		returnValue="{0}GB".format(float(storageSpace/1024/1024))
	return returnValue


count=0
with open('volumes_usage.txt', 'r') as volFile:
	for lines in volFile:
		line=lines.replace(';', '')
		line=line.split(' ')
		used=int(line[6])
		available=int(line[8])
		total=(used+available)
		percent=round(used/float(total), 3)*100
		drive=line[0]
		checkDate=line[3]
		checkTime=line[4]
		usedString=validateNumLen(used)
		totalString=validateNumLen(total)
		output="{0} {1} {2} {3}% ({4}) used of {5}".format(checkDate, checkTime, drive, percent, usedString, totalString)
		with open('volumes.log', 'a+') as log:
			count=count+1
			#print count
			log.write(output+'\n')
