#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import sys  # stdin, stdout, stderr
import os
import socket
import glob
import re

import extract

MAX_PAGES = 3

def getPage(file,page,extractedPages):
  parsed = False
  output = ""
  for line in file:
      if "%%#PAGE" in line and page in line:
        pageName = re.search('%%#PAGE\s(.*)\shttp',line).group(1)
        parsed = True
        output += line
      elif "%%#PAGE" in line and parsed:
        outputFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + pageName.replace(' ','_') + '-'+socket.gethostname()+'-parsed-page.page', 'w+')
        outputFile.write(output)
        outputFile.close()
        output = extract.clearPage(output)
        outputFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + pageName.replace(' ','_') + '-clear-'+socket.gethostname()+'-parsed-page.page', 'w+')
        outputFile.write(output)
        outputFile.close()
        return extractedPages
        # TODO dodělat extrakci pouze jedné stránky
      #elif "%%#DOC" not in line and "%%#PAR" not in line and parsed:
      elif parsed:
        output += line
  return extractedPages

if __name__ == "__main__":
  page = sys.argv[1]
  print page
  allPages = False
  pureText = False
  if len(sys.argv) > 2:
    allPages = True
  if len(sys.argv) > 3:
    pureText = True
  extractedPages = 0

  # parsing data from servers
  for filename in glob.glob(os.path.join('/mnt/data/indexes/wikipedia/enwiki-20150901/collPart*', '*.mg4j')):
    file = open(filename, 'r')
    extractedPages = getPage(file,page,extractedPages)

    if extractedPages > MAX_PAGES:
      print "Zpracování více jak sto stran, ukončuji program..."
      sys.exit(0)

  # end of script
  sys.exit(0)