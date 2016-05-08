#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-

import getopt  # parametry
import glob
import json
import sys  # stdin, stdout, stderr
import re
import os
import subprocess
import socket
import threading

from time import gmtime, strftime
# import XML parse
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch

###############################################################
# Threading class
###############################################################
class myThread (threading.Thread):
  def __init__(self, name, threadID,insertLink):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.insertLink = insertLink
    self.es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)
  def run(self):
    print 'Start thread'
    checkURLwithRedirects(self.es,self.name,self.insertLink)
    print 'End thread'

###############################################################
# Method for raise multiple-thread for entity checking
###############################################################
def checkMultiThreadURL(files,insert):
  d = {}
  counter = 0
  # creating threads
  while counter < len(files):
    d[counter] = myThread(files[counter], counter,insert)
    counter += 1

  counter = 0
  # starts threads
  while counter < len(files):
    d[counter].start()
    counter += 1

  counter = 0
  # join threads
  while counter < len(files):
    d[counter].join()
    counter += 1

class InsertClass:
  es = ''
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self):
      self.checkedEntity = 0
      self.filteredEntity = 0
      self.insertID = 0

  ###############################################################
  # Method for Elastic insert entity
  ###############################################################
  def insertEntity(self,entity, url, sentences, es):
    appereance = '['
    for item in sentences.split('|'):
      appereance += '{"sentence": "'+item.replace('"','')+'"}, '

    appereance = '{"sentences": '+appereance[:-2]+']}'
    #print appereance
    #appereance = json.loads(appereance)
    appereance = json.dumps(appereance)


    # new input
    inputLink = {'id': self.insertID,'host': socket.gethostname(), 'entity' : entity, 'url': url, 'doc': appereance}
    # insert
    es.index(index='xstejs24_extractor', doc_type='withoutURL', id=self.insertID, body=inputLink)
    self.insertID += 1

  ###############################################################
  # Method for split entity files for more thread
  ###############################################################
  def getFiles(self):
    files = []
    for filename in glob.glob(os.path.join('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/ExtractedEntity/', '*.tmp-entity')):
      files.append(filename)
    return files

###############################################################
# Method for check if entity from URL is same as from text
# TODO - chtělo by to trošku vylepšit, uvidíme dle výsledků
###############################################################
def compareEntities(verb,noun,line, interest):
  if noun is 'unknow':
    return True
  heurestic = 0
  for item in verb.split(' '):
    if item in line:
      heurestic += 1
  for item in noun.split(' '):
    if item in line:
      heurestic += 3

  # check if pages are in same interesting
  if not heurestic > len(noun.split(' ')) * 3:
    if interest in noun:
      return True
    else:
      return False
  return True

  #return True if heurestic > len(noun.split(' ')) * 3 else False

###############################################################
# Method for check entity url with extracetd redirected URL form xml dump
###############################################################
def checkURLwithRedirects(es,threadName,insertLink):
  with open(threadName.replace('/ExtractedEntity/','/CheckedLinks/'), 'w+') as outputFile:
    with open(threadName, 'r') as entitySourceFile:
      for line in entitySourceFile:
        entity = re.search('([^\t]+)\t(http[^\t]+)\t([^\t]+)\t([^\n]+)',line)
        entityName = entity.group(1)
        pageURL = entity.group(2)
        entitySentence = entity.group(3)
        interest = entity.group(4)
        url = 'https://en.wikipedia.org/wiki/'+entityName.replace(' ','_')
        #filter for get document
        qbody = {
              "filter": {
                "term":  { "url":url}},

            }
        document = es.search(index='xstejs24_extractor', doc_type='wikilinks', body=qbody)
        # checking
        if document['hits'].get('total') > 0:
          for item in document['hits']['hits']:
            verb = item.get('_source').get('verb').encode('utf-8')
            noun = item.get('_source').get('noun').encode('utf-8')
          if verb == 'unknown' and noun == 'unknown':
            # filre write
            outputFile.write(line)
          elif not compareEntities(verb,noun,entitySentence, interest):
            # filre write
            outputFile.write(line)
            # insert to elastic db - don't use
            #insertLink.insertEntity(entityName,pageURL,entitySentence,es)
          else:
            insertLink.filteredEntity += 1
            #print entityName + ' -> '+verb+' '+noun

        insertLink.checkedEntity += 1
        if insertLink.checkedEntity > 10000:
          sys.exit(0)

###############################################################
# Method for check entity url with extracetd redirected URL form xml dump
###############################################################
def checkURL():
  # new class + db conects
  insertLink = InsertClass()
  es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)
  # opening files
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/entity-non-page.checked', 'w+') as outputFile:
    with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/ExtractedEntity/entity-non-page.check', 'r') as entitySourceFile:
      for line in entitySourceFile:
        entity = re.search('([^\t]+)\t(http[^\t]+)\t([^\t]+)\t([^\n]+)',line)
        if not entity:
          continue
        entityName = entity.group(1)
        pageURL = entity.group(2)
        entitySentence = entity.group(3)
        interest = entity.group(4)
        url = 'https://en.wikipedia.org/wiki/'+entityName.replace(' ','_')
        #filter for get document
        qbody = {
              "filter": {
                "term":  { "url":url}},

            }
        #print qbody
        document = es.search(index='xstejs24_extractor', doc_type='wikilinks', body=qbody)
        #print document
        # checking
        if document['hits'].get('total') > 0:
          for item in document['hits']['hits']:
            verb = item.get('_source').get('verb').encode('utf-8')
            noun = item.get('_source').get('noun').encode('utf-8')
            redirect = item.get('_source').get('redirect')
          if not compareEntities(verb,noun,entitySentence,interest) and not redirect:
            # filre write
            outputFile.write(line)
            # insert to elastic db - don't use
            #insertLink.insertEntity(entityName,pageURL,entitySentence,es)
          else:
            insertLink.filteredEntity += 1
            #print entityName + ' -> '+verb+' '+noun

        else:
          outputFile.write(line)

        insertLink.checkedEntity += 1
        if insertLink.checkedEntity % 100000 == 0:
          print 'Čas: '+strftime("%Y-%m-%d %H:%M:%S", gmtime())
          print 'Prozatím zpracováno: '+str(insertLink.checkedEntity)
          print 'Prozatím vyfiltrováno: '+str(insertLink.filteredEntity)
          print 'Prozatím vloženo: '+str(insertLink.checkedEntity-insertLink.filteredEntity)

        '''if insertLink.checkedEntity % 100000 == 0:
          print 'Prozatím zpracováno: '+str(insertLink.checkedEntity)
          print 'Prozatím vyfiltrováno: '+str(insertLink.filteredEntity)
          print 'Prozatím vloženo: '+str(insertLink.checkedEntity-insertLink.filteredEntity)
          sys.exit(0)'''


# main
if __name__ == "__main__":
  # třída pro insert
  insertLink = InsertClass()
  es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)
  link = []
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())
  #checkMultiThreadURL(insertLink.getFiles(), insertLink)
  checkURL()
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())

  '''x = 0
  es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/ExtractedEntity/entity-non-page.check', 'r') as entitySourceFile:
  #with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/CheckedLinks/'+socket.gethostname()+'/'+socket.gethostname()+'-'+str(0)+'.tmp', 'r') as entitySourceFile:
    #entity-non-page.check
    for line in entitySourceFile:
      item = re.search('([^\t]+)\thttp[^\t]+\t[^\n]+',line)
      url = 'https://en.wikipedia.org/wiki/'+item.group(1).replace(' ','_')
      qbody = {
            "filter": {
              "term":  { "url":url}},
          }
      jsonTest = es.search(index='xstejs24_extractor', doc_type='wikilinks', body=qbody)
      if jsonTest['hits'].get('total') > 0:
        insertLink.filteredEntity += 1
      x += 1
      insertLink.checkedEntity += 1'''


  print 'Vstupní počet entity: '+str(insertLink.checkedEntity)
  print 'Vyfiltrováno z celého souboru: '+str(insertLink.filteredEntity)
  print 'Vloženo: '+str(insertLink.checkedEntity-insertLink.filteredEntity)
  print "Hotovo!"

  sys.exit(0)

