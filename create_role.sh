#!/bin/bash - 
#===============================================================================
#
#          FILE:  create_role.sh
# 
#         USAGE:  create_role.sh {create | delete}
# 
#   DESCRIPTION:  Creates/deletes read-only postgres role
#       OPTIONS:  Edit script for desired role name/passwd
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Colburn Hayden (CH), colburn.hayden@zoomint.com
#       COMPANY: Zoom International, Franklin, TN
#       CREATED: 02.06.2017 11:00:00 CET
#      REVISION:  ---
#===============================================================================

ROLE=colburn #add desired role name
PASSWORD=password #add desired password
DB=callrec #usually always callrec


case "$1" in 
	create) 
		psql -U postgres $DB -c "create role $ROLE login;
		alter role $ROLE with unencrypted password '$PASSWORD';
		grant connect on database $DB to $ROLE;
		grant usage on schema wbsc to $ROLE;
		grant usage on schema callrec to $ROLE;
		grant select on all tables in schema callrec to $ROLE;
		grant select on all tables in schema wbsc to $ROLE;"
		;;
    delete)
	    psql -U postgres $DB -c "revoke connect on database $DB from $ROLE;
		revoke usage on schema wbsc from $ROLE;
		revoke usage on schema callrec from $ROLE;
		revoke select on all tables in schema callrec from $ROLE;
		revoke select on all tables in schema wbsc from $ROLE; 
		drop role $ROLE;"
		;;
		
	*)
		echo "ERROR: usage $0 {delete|create}"
		
esac
exit 0 