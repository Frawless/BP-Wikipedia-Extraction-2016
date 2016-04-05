#!/bin/sh
#Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

server="$(uname -n)-non-page"

#servers_output/entity-non-page.none
fil="/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/$server.check"
outFil="/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/$server.checked"

echo "start..."
echo -n "" > ${outFil}
if [ -f $fil ]
then
  while read line
  do
    entity=$(echo -e "$line" | cut -f-1,2 -d$'\t')
    #echo $entity
    #url=$(echo -e "$line" | cut -f2 -d$'\t')
    if ! grep -q "$entity" ${outFil}
    then
        found=$(grep -n "$entity" $fil | cut -f3 | tr '\n' '|')
        found="$entity\t$url\t$found"
        echo -e ${found::-1} >> ${outFil}
    fi
  done < ${fil}
else
  echo "Missing file: $fil"
fi

echo "Počet entit: $(wc -l $outFil)"

exit