#!/bin/bash -
SCRIPT=$0
DATE=$(date +%Y-%m-%d)
KEY1='CCE_CFG_LoginID'
KEY2=" or key='CCE_CFG_Other_LoginID'"
FILE='/opt/callrec/tmp/agents_no_client.csv'
DB="callrec"

set_query () {
QUERY="copy (select distinct value from couple_extdata where key='$KEY1' $KEY2 and value not in (select distinct value from couple_extdata where key='$KEY1' $KEY2 and cplid in (select cplid from cfiles where cfpath like '%recd%' and start_ts > '$DATE')) and cplid in (select id from couples where start_ts > '$DATE')) to '$FILE' with CSV DELIMITER ',';"
}

if [[ $1 == '' ]]; then
    echo "Expecting Arguments. For help enter: $SCRIPT -h"
    exit 1
fi

while true; do
        case $1 in
        -k|--key )
            KEY1='$OPTARG'
            shift 2
        ;;
        -o|--other-key )
            if [[ $OPTARG == 'NULL' ]]; then
                unset KEY2
            else
                KEY2=" or key='$OPTARG'"
            fi
            shift 2
        ;;
        -f|--output-file )
            FILE='$OPTARG'
            shift 2
        ;;
        -d|--database )
            DB=$OPTARG
            shift 2
        ;;
        -h|--help )
            echo "Usage: $SCRIPT -k <key> -f <path-to-file>
            -h|--help              print this help screen
            -f|--output-file       path to output file
            -k|--key               key to use for agentID
            -o|--other-key         optional key to use for other agentID"
            exit 0
        ;;
        *)
            echo "Invalid option: use $SCRIPT -h for help"
            exit 1
        ;;
    esac
done

set_query
psql -U postgres callrec -c "$QUERY"
