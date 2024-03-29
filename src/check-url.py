#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

###############################################################
# Imports
###############################################################
import sys  # stdin, stdout, stderr
import os
import socket
import re
import shutil
import threading
import glob
import subprocess

###############################################################
# Threading class
###############################################################
class myThread (threading.Thread):
  def __init__(self, name, threadID):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
  def run(self):
    checkURLwithArticles(self.threadID)
    checkURLwithRedirects(self.threadID)

###############################################################
# Method for delete duplicity in enttiy files
# TODO vyřešeno v persons.py
###############################################################
def deleteDuplucity():
  previousLine = ""
  addLine = ""
  lineCounter = 0
  print ("Start deleteDuplicity()...")
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
  os.remove('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/' + socket.gethostname() + '-non-page.tmp-entity')

###############################################################
# Method for split entity files for more thread
###############################################################
def splitFile():
  print ("Start splitFile()...")
  counter = 0
  fileNumber = 0
  fileCounter = 1
  if not os.path.exists('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()):
    print ("Vytvářím složku: "+socket.gethostname())
    os.makedirs('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname())
  if not os.path.exists('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Deleted/'+socket.gethostname()):
    print ("Vytvářím složku: "+socket.gethostname())
    os.makedirs('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Deleted/'+socket.gethostname())
  currentFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(fileNumber)+'.tmp','w+')
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/ExtractedEntity/' + socket.gethostname() + '-non-page.tmp-entity', 'r') as inputFile:
    for line in inputFile:
      counter += 1
      if counter%10000 == 0:
        currentFile.close()
        fileNumber += 1
        currentFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(fileNumber)+'.tmp','w+')
        fileCounter += 1
        #break
      currentFile.write(line)
  # closing files and delting tmp folder
  currentFile.close()
  inputFile.close()
  #return
  return fileCounter

###############################################################
# Methond for re-join created files with checked entities
###############################################################
def reJoinFiles():
  print ("Start reJoinFiles()...")
  # joining checked files
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'-non-page.checked', 'w+') as outfile:
    for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname(), '*.checked')):
      with open(filename) as infile:
         for line in infile:
           outfile.write(line)
  outfile.close()

  # joining checked files
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Deleted/'+socket.gethostname()+'-non-page.deleted', 'w+') as delFile:
    for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Deleted/'+socket.gethostname(), '*.deleted')):
      with open(filename) as infile:
         for line in infile:
           delFile.write(line)
  delFile.close()
  # delete tmp fodlers
  shutil.rmtree('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/',ignore_errors=True)
  shutil.rmtree('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Deleted/'+socket.gethostname()+'/',ignore_errors=True)

###############################################################
# Method for raise multiple-thread for entity checking
###############################################################
def checkMultiThreadURL(fileCount):
  d = {}
  counter = 0
  # creating threads
  while counter < fileCount:
    d[counter] = myThread("Thread-"+str(counter), counter)
    counter += 1

  counter = 0
  # starts threads
  while counter < fileCount:
    d[counter].start()
    counter += 1

  counter = 0
  # join threads
  while counter < fileCount:
    d[counter].join()
    counter += 1

###############################################################
# Method for check if entity from URL is same as from text
# TODO - chtělo by to trošku vylepšit, uvidíme dle výsledků
###############################################################
def compareEntities(verb,noun,line):
  heurestic = 0
  for item in verb.split(' '):
    if item in line:
      heurestic += 1
  for item in noun.split(' '):
    if item in line:
      heurestic += 3
  return True if heurestic > len(noun.split(' ')) * 3 else False

###############################################################
# Method for check entity url from articles URLs from mg4j files
###############################################################
def checkURLwithArticles(threadNumber):
  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.tmp-checked','w+')
  fileDel = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Deleted/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.deleted','w+')
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.tmp', 'r') as entitySourceFile:
    for entity in entitySourceFile:
      entityName = re.search('([^\t]+)[^\n]+',entity).group(1)[:-1]
      entityURL = 'https://en.wikipedia.org/wiki/'+entityName.replace(' ','_')
      # grep info from URL file
      p = subprocess.Popen(['grep','-n', '-s',entityURL,'/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Wikilinks/all-wiki-links.aux'],stdout=subprocess.PIPE)
      output = p.communicate()[0]
      # extract entity info from grep output
      entityInfo = re.search('[^\t]+\t([^\s]+)\s([^\s]+)\n',str(output).replace('\\t','\t').replace('\\n','\n'))
      if entityInfo:
        verb = entityInfo.group(1)
        noun = entityInfo.group(2)
        if not compareEntities(verb, noun, entity): # entity doesn't have own page but another entity with same name has it
          file.write(entity)
        else: # entity already has page on wikipedia
          fileDel.write(entity)
          #fileDel.write(str(output).replace('\\t','\t').replace('\\n','\n')) ???
      else: # entity doesn't have own page
        file.write(entity)
  file.close()
  fileDel.close()
  print ("Dokončena první kontrola odkazů.")

###############################################################
# Method for check entity url with extracetd redirected URL form xml dump
###############################################################
def checkURLwithRedirects(threadNumber):
  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.checked','w+')
  fileDel = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Deleted/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.deleted','a+')
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(threadNumber)+'.tmp-checked', 'r') as entitySourceFile:
    for entity in entitySourceFile:
      entityName = re.search('([^\t]+)[^\n]+',entity).group(1)[:-1]
      entityURL = 'https://en.wikipedia.org/wiki/'+entityName.replace(' ','_')
      # grep info from URL file
      p = subprocess.Popen(['grep','-n', '-s',entityURL,'/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/redirectedLinks.redirect'],stdout=subprocess.PIPE)
      output = p.communicate()[0]
      # check if grep found entity
      if "b''" in str(output):
        fileDel.write(entity)
      else:
        file.write(entity)
  file.close()
  fileDel.close()
  print ("Dokončena druhá kontrola odkazů.")

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  #deleteDuplucity() # delete entity duplicity
  fileCount = splitFile() # split entity file for multi-threading
  checkMultiThreadURL(fileCount)  # create more threads on server for checking entities url on wiki
  reJoinFiles() # re-join splited files

  sys.exit(0)

