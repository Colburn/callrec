import datetime
td = datetime.datetime.now()
yd=td - datetime.timedelta(days=1)
#today=td.strftime("%Y-%m-%d 00:00")
#yester=yd.strftime("%Y-%m-%d 00:00")

import pg

callrec = pg.connect('callrec', 'localhost', 5432, None, None, 'callrec', 'callrec')
evals=callrec.query("select evaluationid from evaluations where qformid in (select qformid from questforms where qftype='SURVEY');")

for i in evals.dictresult():
   new_user=callrec.query("select userid from sc_users where phone in (select to_number from evalcalls where subevaluationid in (select subevaluationid from subevaluation where criteriaid in (select criteriaid from criteria where evaluationid={0})))".format(i['evaluationid']))
   updated=callrec.query("update evaluations set evaluated_user={0} where evaluationid={1}".format(new_user.dictresult()[0]['userid'], i['evaluationid']))
   print updated
