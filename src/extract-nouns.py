#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import sys  # stdin, stdout, stderr
import os
import re

# main
if __name__ == "__main__":
  fileName = "/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/ExtractedEntity/entity-non-page.check"
  nounArray = {}

  file = open(fileName,'r')
  for line in file:
    entity = re.search('([^\t]+)\thttp[^\n]+',line)
    if entity:
      for noun in entity.group(1).split(' '):
        if noun is "":
          continue
        if noun not in nounArray:
          nounArray[noun] = 1
        else:
          nounArray[noun] += 1
  file.close()


  file = open("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/list_of_used_nouns.list",'w+')

  sorted_array = sorted(nounArray.iteritems(), key=lambda x: int(x[1]), reverse=True)
  for key,raw in sorted_array:
      file.write(key+"\t{}".format(raw)+"\n")
    #print key


  sys.exit(0)


