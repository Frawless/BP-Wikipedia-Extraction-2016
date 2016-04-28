#!/usr/bin/env bash

#Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

OPTIND=1

# Initialize our own variables:
page=""
servers="/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers.txt"
pureText=""
allPages=""

# print help
show_help(){
	echo "Usage: $0"
	exit 1
}

while getopts "h" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    esac
done

parallel-ssh -t 0 -i -h $servers -A "python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/run-all.sh"

exit
# End of file