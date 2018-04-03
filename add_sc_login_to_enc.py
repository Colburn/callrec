#DB Variables

import pg

callrecDbName='callrec'
callrecDbUser='wbsc'
callrecDbPasswd='callrec'
callrecDbHost='localhost'
callrecDbPort=5432
wbsc=pg.DB(callrecDbName, callrecDbHost, callrecDbPort, None, None, callrecDbUser, callrecDbPasswd)


encDbName='encourage'
encDbUser='encourage'
encDbPasswd='encourage'
encDbHost='localhost'
encDbPort=5432
enc=pg.DB(encDbName, encDbHost, encDbPort, None, None, encDbUser, encDbPasswd)



sc_users=wbsc.query('select * from sc_users').dictresult()


for i in sc_users:
    enc.query("update users set callcentreid='{0}' where username='{0}'".format(i['login']))
    
callrec.close()
enc.close()





