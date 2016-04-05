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



# THreading class
class myThread (threading.Thread):
    def __init__(self, name, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        print ("Starting " + self.name)
        functionThread(self.name, self.threadID)
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
        print  (counter)
  outputFile.close()
  entityFile.close()
  urlFile.close()

  # clearing *.tmp files
  #for file in glob.glob("/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/*.tmp-entity"):
    #os.remove(file)

# Method for split entity files for more thread
def splitFile():
  counter = 0
  fileNumber = 0
  fileCounter = 1
  if not os.path.exists('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'+socket.gethostname()):
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


def functionThread(threadName, threadNumber):
  #time.sleep(5)
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
  inputFile.close()


def checkMultiThreadURL(fileCount):
  d = {}
  counter = 0
  while counter < fileCount:
    d[counter] = myThread("Thread-"+str(counter), counter)
    counter += 1

  counter = 0
  while counter < fileCount:
    #thread = myThread("Thread-"+str(counter), counter)
    #thread.start()
    d[counter].start()
    counter += 1
  counter = 0
  while counter < fileCount:
    d[counter].join()
    counter += 1

  #funguje
  '''thread0 = myThread("Thread-"+str(counter), 0)
  thread1 = myThread("Thread-"+str(counter), 1)
  thread2 = myThread("Thread-"+str(counter), 2)
  thread0.start()
  thread1.start()
  thread2.start()
  thread0.join()
  thread1.join()
  thread2.join()'''

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

  sys.exit(0)

