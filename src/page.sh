#!/bin/sh
#Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

OPTIND=1

# Initialize our own variables:
page=""
servers="/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers.txt"
pureText=""
fileName=""

# print help
show_help(){
	echo "Usage: $0 -p page -o name [-n]"
	exit 1
}

while getopts "h?o:p:n" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    p)  page=$OPTARG
        ;;
    n)  pureText="yes"
        ;;
    o)  fileName=$OPTARG
        ;;
    esac
done

if [[ -z $page ]] || [[ -z $fileName ]]
then
     show_help
     exit 1
fi

if [ "$pureText" == "yes" ];
then
    parallel-ssh -t 0 -i -h $servers -A "python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/get-page.py $page $fileName isSet"
else
    parallel-ssh -t 0 -i -h $servers -A "python /mnt/minerva1/nlp/projects/ie_from_wikipedia7/src/get-page.py $page $fileName"
fi

exit
# End of file