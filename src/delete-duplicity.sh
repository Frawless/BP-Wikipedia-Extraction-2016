#!/bin/sh
#Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

fil=/mnt/minerva1/nlp/projects/ie_from_wikipedia7/test.txt
outFil=/mnt/minerva1/nlp/projects/ie_from_wikipedia7/test-sorted.txt

echo "start..."
echo -n "" > ${outFil}
if [ -f $fil ]
then
  echo "file exists"
  while read line
  do
    echo $line
    entity=$(echo -e "$line" | cut -f1 -d$'\t')
    url=$(echo -e "$line" | cut -f2 -d$'\t')
    echo "Vypisuji entitu a url:"
    echo $entity
    echo $url
    if ! grep -q "$entity" ${outFil}
    then
        echo "zápis do souboru"
        found=$(grep -n "$entity" $fil | cut -f3 | tr '\n' '|')
        echo "nález:"
        echo $found
        found="$entity\t$url\t$found"
        echo -e ${found::-1} >> ${outFil}
    fi
    echo "po zapsání"
  done < ${fil}

else
  echo "file doesn't exists"
fi

exit