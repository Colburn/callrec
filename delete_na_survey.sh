DB_ADDR="localhost"
QUERY="delete from evaluations where evaluationid not in (select evaluationid from evaluations where evaluationid in (
        select evaluationid from criteria where criteriaid in (
                select criteriaid from subevaluation where subevaluationid in (
                        select subevaluationid from evalanswers where answerid in (
                                select answerid from answers where compliance!='NOT_APPLICABLE')
                        )
                )
        )) and evalstatus='FINISHED' and qformid in (
select qformid from questforms where qftype='SURVEY');"

psql -U postgres callrec -h "${DB_ADDR}" -c "${QUERY}";
