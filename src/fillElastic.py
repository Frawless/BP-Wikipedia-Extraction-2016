#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-

import getopt  # parametry
import sys  # stdin, stdout, stderr
import re
import os
import subprocess
import socket

# import XML parse
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch

###############################################################
# Constants
###############################################################
PathPrefix = '/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'

class InsertClass:
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self):
      self.STAT = 'statistic'
      self.DOCTYPE = 'wikilinks'
      self.IDXPROJ = 'xstejs24_extractor'
      self.linkID = 0
      self.entityID = 0
  ###############################################################
  # Method for Elastic insert Wikilinks
  ###############################################################
  def insertWikilinks(self,link,es):
    # new input
    inputLink = {'id': str(self.linkID),'url': link[0], 'redirect' : False, 'url-redirected': 'none', 'verb': link[1], 'noun': link[2] }
    # insert
    es.index(index=self.IDXPROJ, doc_type=self.DOCTYPE, id=str(self.linkID), body=inputLink)
    self.linkID += 1

  ###############################################################
  # Method for Elastic insert redirected links
  ###############################################################
  def insertRedirects(self,link,es):
    # new input
    inputLink = {'id': str(self.linkID),'url': link[0], 'redirect' : True, 'url-redirected': link[1], 'verb': 'none', 'noun': 'none' }
    # insert
    es.index(index=self.IDXPROJ, doc_type=self.DOCTYPE, id=str(self.linkID), body=inputLink)
    self.linkID += 1

  ###############################################################
  # Method for Elastic insert statistics
  ###############################################################
  def insertStats(self,data,es):
    # new input
    inputLink = {'id': data[0],'host': data[1], 'time' : data[2], 'articles': data[3], 'entity': data[4] }
    # insert
    es.index(index=self.IDXPROJ, doc_type=self.STAT, id=data[0], body=inputLink)
    self.linkID += 1

  ###############################################################
  # Method for parse extraction file with stats
  ###############################################################
  def parseStatsFile(self,es):
    data = []
    x = 0
    data.append(x)
    with open(PathPrefix+'Statistic/statistic.stats') as statsFile:
      for line in statsFile:
        stats = re.search('([\d|\.]+)',line)
        if 'Server:' in line and stats:
          data.append(line.replace('# Server:\t','').replace('\n',''))
        if 'Execution time:' in line and stats:
          data.append(stats.group(1))
        if 'Parsed Articles:' in line and stats:
          data.append(stats.group(1))
        if 'Extracted Entity:' in line and stats:
          data.append(stats.group(1))
        if len(data) > 4:
          self.insertStats(data,es)
          data = []
          x += 1
          data.append(x)


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
    inputLink = {'id': socket.gethostname()+'-'+str(self.filteredEntity),'host': socket.gethostname(), 'entity' : entity, 'url': url, 'doc': appereance}
    # insert
    es.index(index=IDXPROJ, doc_type=DOCTYPE, id=socket.gethostname()+'-'+str(self.filteredEntity), body=inputLink)
    self.filteredEntity += 1'''

###############################################################
# Method for insert data
###############################################################
def insertData():
  # nastavení databáze elastic search
  HOST        = 'athena1.fit.vutbr.cz'
  PORT        = 9200
  DOCTYPE     = 'wikilinks'
  IDXPROJ     = 'xstejs24_extractor'

  insertLink = InsertClass()

  link = []

  # DB connect
  es = Elasticsearch(host=HOST, port=PORT)
  print 'Vkládám statistiky...'
  insertLink.parseStatsFile(es)

  print 'Vkládám současné odkazy...'
  # insert extracted links
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Wikilinks/all-wiki-links.articles') as linkFile:
    for line in linkFile:
      item = re.search('([^\t]+)\t([^ ]+) ([^\n]+)\n',line)
      link.append(item.group(1))
      link.append(item.group(2))
      link.append(item.group(3))

      insertLink.insertWikilinks(link,es)
      link = []

  print 'Vkládám přesměrované odkazy...'
  # insert redirected
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Wikilinks/redirectedLinks.redirect') as linkFile:
    for line in linkFile:
      item = re.search('([^\t]+)\t([^\n]+)\n',line)
      link.append(item.group(1))
      link.append(item.group(2))

      insertLink.insertRedirects(link,es)
      link = []

# main
if __name__ == "__main__":
  insertData()
  print "Done!"
  sys.exit(0)
