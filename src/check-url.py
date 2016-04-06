#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import sys  # stdin, stdout, stderr
import os
import socket
import re
import shutil

import threading
import glob

import urllib.request
import urllib.error


import urllib

import subprocess
from subprocess import Popen, PIPE


# THreading class
class myThread (threading.Thread):
    def __init__(self, name, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print ("Starting " + self.name)
        #functionThread(self.name, self.threadID)
        checkURL(self.threadID)
        print ("Exiting " + self.name)


def deleteDuplucity():
  previousLine = ""
  addLine = ""
  lineCounter = 0
  print ("Start duplicity...")
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
  print ("End duplicity...")
  #os.remove('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + socket.gethostname() + '-non-page.tmp-entity')

# Method for split entity files for more thread
def splitFile():
  counter = 0
  fileNumber = 0
  fileCounter = 1
  print ("Existuje složka?")
  if not os.path.exists('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()):
    print ("Vytvářím složku")
    os.makedirs('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname())
  currentFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(fileNumber)+'.tmp','w+')
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + socket.gethostname() + '-non-page.check', 'r') as inputFile:
    for line in inputFile:
      counter += 1
      #if counter == 6000: # for testing
        #break
      if counter%2000 == 0:
        currentFile.close()
        fileNumber += 1
        currentFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(fileNumber)+'.tmp','w+')
        fileCounter += 1
      currentFile.write(line)
  # closing files and delting tmp folder
  currentFile.close()
  inputFile.close()

  #return
  return fileCounter

# Methond for re-join created files with checked entities
def reJoinFiles():
  # joining checked files
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'-non-page.checked', 'w+') as outfile:
    for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname(), '*.checked')):
      with open(filename) as infile:
         for line in infile:
           outfile.write(line)
  outfile.close()

  # joining checked files
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'-non-page.deleted', 'w+') as delFile:
    for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname(), '*.deleted')):
      with open(filename) as infile:
         for line in infile:
           delFile.write(line)
  delFile.close()
  # delete tmp dir -> toto se musí provést až po skončení vláken!!!
  shutil.rmtree('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/')

# Method for thread
def functionThread(threadName, threadNumber):
  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.checked','w+')
  fileDel = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.deleted','w+')
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.tmp', 'r') as inputFile:
    for line in inputFile:
      link = 'https://en.wikipedia.org/wiki/'+re.search('([^\t]+)\thttp[^\n]+',line).group(1).replace(' ','_')
      #print (link[:-1])
      link = urllib.request.quote(link[:-1], "/,.;:+-*%")
      try:
          urllib.request.urlopen(link)
          fileDel.write(line)
      except urllib.error.HTTPError as e:
          if e.code != 200:
            file.write(line)


  file.close()
  fileDel.close()

# Method for raise multiple-thread for entity checking
def checkMultiThreadURL(fileCount):
  d = {}
  counter = 0
  while counter < 1:
    d[counter] = myThread("Thread-"+str(counter), counter)
    counter += 1

  counter = 0
  while counter < 1:
    d[counter].start()
    counter += 1
  counter = 0
  while counter < 1:
    d[counter].join()
    counter += 1


def compareEntities(verb,noun,line):
  heurestic = 0
  for item in verb.split(' '):
    if item in line:
      heurestic += 1
  for item in noun.split(' '):
    if item in line:
      heurestic += 4

  return True if heurestic > 4 else False


# metod for check entity url
def checkURL(threadNumber):
  verb = ""
  noun = ""

  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.checked','w+')
  fileDel = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.deleted','w+')
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.tmp', 'r') as entitySourceFile:
    for entity in entitySourceFile:
      print (entity)
      write = True
      with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/all-wiki-links.aux', 'r') as entityCheckFile:
        for line in entityCheckFile:
          entityName = re.search('([^\t]+)[^\n]+',entity).group(1)[:-1]
          entityURL = 'https://en.wikipedia.org/wiki/'+entityName.replace(' ','_')
          if not re.search('(http[^\t]+)\t[^\n]+',line):
            continue
          entityInfo = re.search('http[^\t]+\t([^\s]+)\s([^\n]+)',line)
          if entityURL in line:
            verb = entityInfo.group(1)
            noun = entityInfo.group(2)
            if not compareEntities(verb, noun, entity):
              # entity doesn't have own page but another entity with same name has it
              print ("Zápis do file s FALSE")
              file.write(entity)
              write = False
            else:
              # entity already has page on wikipedia
              print ("Zápis do fileDel")
              fileDel.write(entity)
              write = False
            break
        if write:
          # entity doesn't have own page
          print ("Zápis do file s true")
          file.write(entity)

    print ("Dokončen entity file")
  file.close()
  fileDel.close()

#main
if __name__ == "__main__":
  # delete entity duplicity
  #deleteDuplucity()
  # checking url
  #checkURL()
  # TEST
  fileCount = splitFile()
  checkMultiThreadURL(fileCount)
  reJoinFiles()
  #checkURL(1)

  sys.exit(0)

