
#!/usr/bin/python 
#===============================================================================
#
#          FILE:  whisper_repair.py
# 
#         USAGE:   python ./whisper_repair.sh 
# 
#   DESCRIPTION:  Workaround for bug which causes call external data to attach
#                 to whisper segment of calls, but not the actual call. Copies
#                 external data from the whisper calls to the actual couple. 
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Colburn Hayden (CH), colburn.hayden@zoomint.com
#       COMPANY: Zoom International, Prague
#       CREATED: N/A
#      REVISION:  ---
#===============================================================================

import pg, subprocess                                                                                                                                                                                       
callrec = pg.connect('callrec', 'localhost', 5432, None, None, 'callrec', 'callrec')                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                                      
whisper=''                                                                                                                                                                                                  
callrecdict=''                                                                                                                                                                                              
created_ts="select distinct cplid, created_ts from couple_extdata where cplid='{0}' order by cplid, created_ts asc;"                                                                                        
count=callrec.query("select count(*) from couple_extdata where value in (select value from couple_extdata group by value having count(value) > 2) and key='JTAPI_CISCO_ID';").dictresult()[0]['count']      
n=0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
offset=0                                                                                                                                                                                                    
processed=0                                                                                                                                                                                                 
log=''                                                                                                                                                                                                      
log1=''                                                                                                                                                                                                     
def findCalls():                                                                                                                                                                                            
  global whisper, callrecdict, offset                                                                                                                                                                       
  whisper="select * from couple_extdata where value in (select value from couple_extdata group by value having count(value) > 2) and key='JTAPI_CISCO_ID' order by value, cplid desc limit 40 offset {0};".f
ormat(offset)                                                                                                                                                                                               
  callrecdict=callrec.query(whisper).dictresult()                                                                                                                                                           
  print "Finding calls: {0}".format(whisper)




def processWhisper():                                                                                                                                                                                       
  global n, m, cplid, callrecdict, log, log1                                                                                                                                                                
  for i in callrecdict:                                                                                                                                                                                     
    if n < len(callrecdict):                                                                                                                                                                                
      cplids=[callrecdict[n]]                                                                                                                                                                               
      for z in callrecdict:                                                                                                                                                                                 
        if z['value'] == cplids[0]['value']:                                                                                                                                                                
          cplids.append(z)                                                                                                                                                                                  
                                                                                                                                                                                                            
      for cpl in cplids:                                                                                                                                                                                    
        for cpls in cplids:                                                                                                                                                                                 
          if cpls['cplid'] != cpl['cplid']:                                                                                                                                                                 
            keys=callrec.query("select key,value from couple_extdata lo where cplid='{0}' and not exists (select key from couple_extdata hi where cplid='{1}' and lo.key=hi.key);".format(cpls['cplid'], cpl
['cplid'])).dictresult()                                                                                                                                                                                    
            keys2=callrec.query("select key,value from couple_extdata low where cplid='{0}' and not exists (select key from couple_extdata high where cplid='{1}' and low.key=high.key);".format(cpl['cplid'
], cpls['cplid'])).dictresult()                                                                                                                                                                             
            if len(keys) != 0:                                                                                                                                                                              
              for y in keys:                                                                                                                                                                                
                callrec.query("insert into couple_extdata (cplid, key, value, created_ts) values ('{0}', '{1}', $${2}$$, '{3}');".format(cpl['cplid'], y['key'], y['value'], str(callrec.query(created_ts.fo
rmat(cpl['cplid'])).dictresult()[0]['created_ts'])))                                                                                                                                                        
                #print "Added Data: {0}:{1} to couple: {2}".format(y['key'], y['value'], cpl['cplid'])                                                                                                       
                                                                                                                                                                                                            
            if len(keys2) != 0:                                                                                                                                                                             
              for d in keys2:                                                                                                                                                                               
                callrec.query("insert into couple_extdata (cplid, key, value, created_ts) values ('{0}', '{1}', $${2}$$, '{3}');".format(cpls['cplid'], d['key'], d['value'], str(callrec.query(created_ts.f
ormat(cpls['cplid'])).dictresult()[0]['created_ts'])))                                                                                                                                                      
                #print "Added Data: {0}:{1} to couple: {2}".format(d['key'], d['value'], cpls['cplid'])                                                                                                                                                                                                            
                                                                                                                                                                                  
    n+=1                                                                                                                                                                                                    
    m+=0                                                                                                                                                                                                    
                                                                                                                                                       
                                                                                                                                                                                                            
                                                                                                                                                                                                            
while count >= 0:                                                                                                                                                                                           
  findCalls()                                                                                                                                                                                               
  processWhisper()                                                                                                                                                                                          
  count=count-40                                                                                                                                                                                            
  offset+=40   
