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

class InsertClass:
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self):
      self.checkedEntity = 0
      self.filteredEntity = 0
      self.insertID = 0

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
###############################################################
def compareEntities(verb,noun,line, interest):
  if noun is 'unknow' or noun is 'none':
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
    for item in interest.split(' '):
      if item in noun:
        return True
    else:
      return False
  return True

###############################################################
# Method for check entity url with url in db
###############################################################
def checkURL(PathPrefix):
  shorterName = ''
  # new class + db conects
  insertLink = InsertClass()
  es = Elasticsearch(host='athena1.fit.vutbr.cz', port=9200)
  # opening files
  # TODO - nastavit správně pro celkový systém!
  with open(PathPrefix+'CheckedLinks/entity-non-page.checked', 'w+') as outputFile:
  #with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/results/Origins_of_the_American_Civil_War_vystup_extrakce.checked', 'w+') as outputFile:
    with open(PathPrefix+'ExtractedEntity/entity-non-page.check', 'r') as entitySourceFile:
    #with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/results/Origins_of_the_American_Civil_War_vystup_extrakce.entity', 'r') as entitySourceFile:
      for line in entitySourceFile:
        entity = re.search('([^\t]+)\t(http[^\t]+)\t([^\t]+)\t([^\n]+)',line)
        if not entity:
          continue
        entityName = entity.group(1)
        pageURL = entity.group(2)
        interest = entity.group(3)
        entitySentence = entity.group(4)
        url = 'https://en.wikipedia.org/wiki/'+entityName.replace(' ','_')
        # find in db
        document = getDocument(es,url)
        # checking
        if document['hits'].get('total') > 0:
          checkDocument(document, line, outputFile, insertLink,entitySentence, interest)
        elif '.' in entityName:
          for item in entityName.split(' '):
            if '.' not in item:
              shorterName += item+' '
          if shorterName[:-1].replace(' ','_') in url or len(re.findall(' ',shorterName[:-1])) < 2:
            insertLink.checkedEntity += 1
            outputFile.write(line)
            continue
          url ='https://en.wikipedia.org/wiki/'+shorterName[:-1].replace(' ','_')
          #######################################################################
          # find in db
          document = getDocument(es,url)
          # checking
          if document['hits'].get('total') > 0:
            checkDocument(document, line, outputFile, insertLink,entitySentence, interest)
          else:
            outputFile.write(line)
          #######################################################################
        else:
          outputFile.write(line)

        insertLink.checkedEntity += 1
        if insertLink.checkedEntity % 1000000 == 0:
          print 'Čas: '+strftime("%Y-%m-%d %H:%M:%S", gmtime())
          print 'Prozatím zpracováno: '+str(insertLink.checkedEntity)
          print 'Prozatím vyfiltrováno: '+str(insertLink.filteredEntity)
          print 'Prozatím vloženo: '+str(insertLink.checkedEntity-insertLink.filteredEntity)

###############################################################
# Method for check founded document from db and write output
###############################################################
def checkDocument(document, line, outputFile, insertLink,entitySentence, interest):
  for item in document['hits']['hits']:
    verb = item.get('_source').get('verb').encode('utf-8')
    noun = item.get('_source').get('noun').encode('utf-8')
    redirect = item.get('_source').get('redirect')
  if not compareEntities(verb,noun,entitySentence,interest) and not redirect:
    # file write
    outputFile.write(line)
  else:
    insertLink.filteredEntity += 1

###############################################################
# Method for create filter
###############################################################
def getDocument(es, url):
  #filter for get document
  qbody = {
        "filter": {
          "term":  { "url":url}},

      }
  return es.search(index='xstejs24_extractor', doc_type='wikilinks', body=qbody,request_timeout=30)

# main
if __name__ == "__main__":
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())
  checkURL()
  print strftime("%Y-%m-%d %H:%M:%S", gmtime())

  sys.exit(0)

