#!/usr/bin/env bash
#Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

time=$(date +"%T")
echo "Start: $now"
bash page.sh -p List_of_Latin_words_with_English_derivatives -o List_of_Latin_words_with_English_derivatives
bash page.sh -p List_of_Latin_words_with_English_derivatives -o List_of_Latin_words_with_English_derivatives-n -n

echo "latin-words->done: $now"
bash page.sh -p Belarus_Free_Theatre -o Belarus_Free_Theatre
bash page.sh -p Belarus_Free_Theatre -o Belarus_Free_Theatre-n -n

echo "Belarus->done: $now"
bash page.sh -p Manchester_Eagles -o Manchester_Eagles
bash page.sh -p Manchester_Eagles -o Manchester_Eagles-n -n

echo "Eagles->done: $now"
bash page.sh -p List_of_most_popular_given_names_by_state_in_the_United_States -o List_of_most_popular_given_names_by_state_in_the_United_States
bash page.sh -p List_of_most_popular_given_names_by_state_in_the_United_States -o List_of_most_popular_given_names_by_state_in_the_United_States-n -n

echo "Names->done: $now"