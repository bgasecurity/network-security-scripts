#!/usr/bin/env bash

RESET=`tput sgr0`
RED=`tput setaf 1`
GREEN=`tput setaf 2`

function usage() {
	echo "Usage: $0 [ -f <target_file>  -w <timeout> -t threat_count ]" 1>&2
	exit 1
}


while getopts ":f:w:t:" p; do
	case "${p}" in
		f)
			f=${OPTARG}
			;;
		w)																				      w=${OPTARG}
			;;
		t)
			t=${OPTARG}
			;;		
		*)
			usage
			;;
		esac
done


shift $((OPTIND-1))
if [ -z "${f}" ] || [ -z "${w}" ] || [ -z "${t}" ]
then
	usage
fi

THREAT="${t}"
IP_FILE="${f}"
TIMEOUT="${w}"


if [ ! -f $IP_FILE ]
then
	echo "File: $IP_FILE Doesn't Exists !!!"
	exit 1	
fi


function do_memcached() {
	
	ip="$1"

	result_file="$(mktemp /tmp/$USER.XXXXXX)"      
	printf '\0\x01\0\0\0\x01\0\0stats\r\n' | nc -nvvu $ip 11211 -w $TIMEOUT  >$result_file  2>$result_file
	
	grep -Eaq "^\ssent\s[0-9]+,\srcvd\s[1-9]+" $result_file 
	if [ $? -eq 0 ]
	then
		sent="`grep -Ea "^\ssent\s[0-9]+,\srcvd\s[1-9]+" $result_file | cut -d "," -f1 | cut -d " " -f3`"
		recv="`grep -Ea "^\ssent\s[0-9]+,\srcvd\s[1-9]+" $result_file | cut -d "," -f2 | cut -d " " -f3`"

		result=$(($recv/$sent))
		echo "[${GREEN}OK${RESET}] -> $ip : $recv/$sent=$result"
	else
		echo "[${RED}NOT${RESET}] -> $ip"
	fi															 
	
	rm -rf $result_file
	
}


function main() {

	cat $IP_FILE | while read -r ip
	do
		while [ 1 ]
		do
			proc_count="`ps -ef | grep -v grep | grep -E "nc -nvvu.*11211" | wc -l`"
			if [ $(($proc_count)) -gt $(($THREAT-1)) ]
			then
				sleep 0.5
			else
				break
			fi
		done

		do_memcached "$ip" &
	done
}

main

