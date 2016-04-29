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

class InsertClass:
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self):
      self.linkID = 0
      self.entityID = 0
  ###############################################################
  # Method for Elastic insert Wikilinks
  ###############################################################
  def insertWikilinks(self,link,es):
    # new input
    inputLink = {'id': socket.gethostname()+'-'+str(self.linkID),'url': link[0], 'redirect' : False, 'url-redirected': 'none', 'verb': link[1], 'noun': link[2] }
    # insert
    es.index(index=IDXPROJ, doc_type=DOCTYPE, id=socket.gethostname()+'-'+str(self.linkID), body=inputLink)
    self.linkID += 1

  ###############################################################
  # Method for Elastic insert redirected links
  ###############################################################
  def insertRedirects(self,link,es):
    # new input
    inputLink = {'id': socket.gethostname()+'-'+str(self.linkID),'url': link[0], 'redirect' : True, 'url-redirected': link[1], 'verb': 'none', 'noun': 'none' }
    # insert
    es.index(index=IDXPROJ, doc_type=DOCTYPE, id=socket.gethostname()+'-'+str(self.linkID), body=inputLink)
    self.linkID += 1

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
  es = Elasticsearch(host=HOST, port=PORT)
  print 'Vkládám současné odkazy...'
  # insert extracted links
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Wikilinks/all-wiki-links.aux') as linkFile:
    for line in linkFile:
      item = re.search('([^\t]+)\t([^ ]+) ([^\n]+)\n',line)
      link.append(item.group(1))
      link.append(item.group(2))
      link.append(item.group(3))

      insertLink.insertWikilinks(link,es)
      link = []

  print 'Vkládám přesměrované odkazy...'
  # insert redirected
  with open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/redirectedLinks.redirect') as linkFile:
    for line in linkFile:
      item = re.search('([^\t]+)\t([^\n]+)\n',line)
      link.append(item.group(1))
      link.append(item.group(2))

      insertLink.insertRedirects(link,es)
      link = []

  print "Hotovo!"

  sys.exit(0)
