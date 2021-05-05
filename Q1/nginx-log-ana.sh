#!/bin/bash
PROG=`basename $0`
FILE=$1
function Usage() {
    cat <<EOF
This tool is to do some simple analytics to Nginx access log.

Arguments
    log file name in gz    [Required]: The name of the access log file
                                       in gz format

Example
    $PROG "access.log.gz"
EOF
}

#Start from here
if [ $# -ne 1 ]; then
    echo "Illegal number of parameters."
    Usage
else 
    echo "--------------------------"
    echo "Total HTTP request records"
    echo "--------------------------"
    zgrep '-' $FILE | wc -l
    
    echo "------------------------------------------------------------"
    echo "Top-10 hosts made requests from 2019-Jun-10 00:00 to 2019-Ju"
    echo "n-19 23:59, inclusively"
    echo "------------------------------------------------------------"
    zgrep '-' $FILE |awk -vDate=`echo "[10/Jun/2019:00:00:00"` -vDate2=`echo "[19/Jun/2019:23:59:59"` '$4 >= Date && $4 <= Date2 { print $1 }' |sort |uniq -c | sort -rn |head -10 |awk '{print  $2}'
    
    echo "-----------------------------------------------"
    echo "The country with most requests originating from"
    echo "-----------------------------------------------"
    zgrep '-' $FILE | awk '{ print $1 }' > ip.txt
    if ! command -v geoiplookup &> /dev/null
    then
        echo "geoiplookup could not be found, going to install..."
        if [ "$(. /etc/os-release; echo $NAME)" = "Ubuntu" ]; then
            sudo apt-get update
            sudo apt-get install geoip-bin -y
        else
            sudo yum install epel-release -y
            sudo yum makecache
            sudo yum install geoip -y
        fi
    fi
    if [[ -f country.txt ]]; then
        rm -f country.txt
        touch country.txt
    else
        touch country.txt
    fi
    while read line
    do
        geoiplookup $line >>country.txt
        #curl -Ssl ifconfig.co/country?ip=$line >> country.txt
    done < ./ip.txt
    cat country.txt | grep -v "can't" |awk -F':' '{ print $2 }'| awk -F',' '{ for (i=2; i<=NF; i++) printf "%s ", $i; print "" }' |sort| uniq -c | sort -rn | head -1 |awk '{ for (i=2; i<=NF; i++) printf "%s ", $i; print "" }'
fi