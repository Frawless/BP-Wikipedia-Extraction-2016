#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-

import getopt  # parametry
import sys  # stdin, stdout, stderr
import re
import os
import subprocess
import socket
import threading

# import XML parse
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch

###############################################################
# Threading class
###############################################################
class myThread (threading.Thread):
  def __init__(self, name, threadID,insert):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.insert = insert
  def run(self):
    print 'Start thread'
    checkURLwithRedirects(self.threadID,self.insert)
    print 'End thread'

###############################################################
# Method for raise multiple-thread for entity checking
###############################################################
def checkMultiThreadURL(fileCount,insert):
  d = {}
  counter = 0
  # creating threads
  while counter < fileCount:
    d[counter] = myThread("Thread-"+str(counter), counter,insert)
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
# Method for check entity url with extracetd redirected URL form xml dump
###############################################################
def checkURLwithRedirects(threadNumber,insert):
  x = 0
  es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-XX'+str(threadNumber)+'.tmp', 'r') as entitySourceFile:
    for line in entitySourceFile:
      item = re.search('([^\t]+)\thttp[^\t]+\t[^\n]+',line)
      url = 'https://en.wikipedia.org/wiki/'+item.group(1).replace(' ','_')

      qbody = {
            "filter": {
              "term":  { "url":url}},

          }
      jsonTest = es.search(index='xstejs24_extractor', doc_type='wikilinks', body=qbody)
      if jsonTest['hits'].get('total') > 0:
        insertLink.entityID += 1

      x += 1
      insertLink.linkID += 1
      #if insertLink.linkID > 1000:
       # sys.exit(0)
      #print 'vlakno: '+str(threadNumber)+' společné id: '+str(insertLink.linkID)+' x: '+str(x)

class InsertClass:
  es = ''
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self):
      self.linkID = 0
      self.entityID = 0

  ###############################################################
  # Method for Elastic insert entity
  ###############################################################
  '''def insertEntity(self,entity, url, sentences):

    for item in sentences.split('|'):
      appereance += '{"sentence": "'+item.replace('"','')+'"}, '

    appereance = '{"sentences": '+appereance[:-2]+']}'
    #print appereance
    #appereance = json.loads(appereance)
    appereance = json.dumps(appereance)

    # DB connect
    es = Elasticsearch(host=HOST, port=PORT)
    # new input
    inputLink = {'id': socket.gethostname()+'-'+str(self.entityID),'host': socket.gethostname(), 'entity' : entity, 'url': url, 'doc': appereance}
    # insert
    es.index(index=IDXPROJ, doc_type=DOCTYPE, id=socket.gethostname()+'-'+str(self.entityID), body=inputLink)
    self.entityID += 1'''



  ###############################################################
  # Method for split entity files for more thread
  ###############################################################
  def splitFile(self):
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
    currentFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-XX'+str(fileNumber)+'.tmp','w+')
    with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(fileNumber)+'.tmp', 'r') as inputFile:
      for line in inputFile:
        counter += 1
        if counter%3000 == 0:
          currentFile.close()
          fileNumber += 1
          currentFile = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-XX'+str(fileNumber)+'.tmp','w+')
          fileCounter += 1
          #break
        currentFile.write(line)
    # closing files and delting tmp folder
    currentFile.close()
    inputFile.close()
    #return
    return fileCounter

# main
if __name__ == "__main__":
  # nastavení databáze elastic search
  HOST        = 'athena1.fit.vutbr.cz'
  PORT        = 9200
  DOCTYPE     = 'wikilinks'
  IDXPROJ     = 'xstejs24_extractor'

  insertLink = InsertClass()

  link = []

  # DB connect
  #insertLink.es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)

  checkMultiThreadURL(insertLink.splitFile(), insertLink)

  '''x = 0
  es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(0)+'.tmp', 'r') as entitySourceFile:
    for line in entitySourceFile:
      item = re.search('([^\t]+)\thttp[^\t]+\t[^\n]+',line)
      url = 'https://en.wikipedia.org/wiki/'+item.group(1).replace(' ','_')

      qbody = {
            "filter": {
              "term":  { "url":url}},

          }
      jsonTest = es.search(index='xstejs24_extractor', doc_type='wikilinks', body=qbody)
      if jsonTest['hits'].get('total') > 0:
        insertLink.entityID += 1

      x += 1
      insertLink.linkID += 1'''



  print 'Vyfiltrováno z celého souboru: '+str(insertLink.entityID)
  print "Hotovo!"

  sys.exit(0)
