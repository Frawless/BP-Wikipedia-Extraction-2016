#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import sys  # stdin, stdout, stderr
import os
import subprocess
import socket
import glob
import re

def deleteDuplucity():
  previousLine = ""
  addLine = ""
  lineCounter = 0
  print "Start duplicity..."
  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + socket.gethostname() + '-non-page.tmp-entity', 'r')
  outfile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + socket.gethostname() + '-non-page.check', 'w+')
  for line in file:
    if line is "":
      continue
    if addLine is "":
      addLine = line
    entity = re.search('([^\t]+)\thttp[^\t]+\t([^\n]+)',line)
    if entity:
      if entity.group(1) in previousLine:
        addLine = addLine[:-1]+"|"+entity.group(2)+"\n"
      elif previousLine is not "":
        outfile.write(addLine)
        addLine = ""
        lineCounter += 1
    previousLine = line
  outfile.close()
  file.close()
  print "End duplicity..."
  #os.remove('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + socket.gethostname() + '-non-page.tmp-entity')


def splitFiles():
  os.makedirs('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname())



# metod for check entity url
def checkURL():
  counter = 0
  # check url
  outputFile = open("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/" + socket.gethostname() + "-non-page.checked", 'w+')
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+ socket.gethostname() + '-non-page.check', 'r') as entityFile:
    for entity in entityFile:
      counter += 1
      with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/all-wiki-links.aux', 'r') as urlFile:
        writeEntity = True
        for url in urlFile:
          entityLink = "https://en.wikipedia.org/wiki/"+re.search('([^\t]+)\t[^\n]+',entity).group(1).replace(' ','_')
          if entityLink[-1:] == '_':
            entityLink = entityLink[:-1]

          #print "URL: "+url+"# -> LINK: "+entityLink+"#"
          if url[:-1] == entityLink:
            writeEntity = False
            #print "hoho"
            break
        if writeEntity:
          outputFile.write(entity)
        print  counter
  outputFile.close()
  entityFile.close()
  urlFile.close()

  # clearing *.tmp files
  #for file in glob.glob("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/*.tmp-entity"):
    #os.remove(file)


#main
if __name__ == "__main__":
  # delete entity duplicity
  deleteDuplucity()
  # checking url
  #checkURL()
  sys.exit(0)

