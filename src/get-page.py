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

def getPage(file,page):
  parsed = False
  output = ""
  for line in file:
      if "%%#PAGE" in line and page in line:
        parsed = True
        output += line
      elif "%%#PAGE" in line and parsed:
        return output
      elif "%%#DOC" not in line and "%%#PAR" not in line and parsed:
        output += line

if __name__ == "__main__":
  page = sys.argv[1]
  outputFile = sys.argv[2]
  pureText = False
  if len(sys.argv) > 3:
    pureText = True
  extractedPage = ""
  # output file name
  outputFileName = "/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/" + outputFile + "-"+socket.gethostname()+"-parsed-page.page"
  # parsing data from servers
  for filename in glob.glob(os.path.join('/mnt/data/indexes/wikipedia/enwiki-20150901/collPart*', '*.mg4j')):
    file = open(filename, 'r')
    extractedPage = getPage(file,page)
    # page was found
    if extractedPage is None:
      extractedPage = ""
    if len(extractedPage) > 0:
      extractedPage = extract.clearPage(extractedPage)
      # pure text extract
      if pureText:
        extractedPage = re.sub(r'\|[^\]]+\]\]', '',extractedPage).replace('[[', '')
      # output to file
      outputFile = open(outputFileName, 'w+')
      outputFile.write(extractedPage)
      outputFile.close()
      sys.exit(0)

  # end of script
  sys.exit(0)