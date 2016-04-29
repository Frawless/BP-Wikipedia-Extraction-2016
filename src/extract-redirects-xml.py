#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-

import getopt  # parametry
import sys  # stdin, stdout, stderr
import re
import os
import subprocess

# import XML parse
import xml.etree.ElementTree as ET
from elasticsearch import Elasticsearch

class InsertRedirect:
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self):
      self.linkID = 0
  ###############################################################
  # Method for Elastic insert Wikilinks
  ###############################################################
  def insertWikilinks(self,url, urlRedirect, es):

    # new input
    inputLink = {'id': 'redirected'+str(self.linkID), 'url': url, 'redirect' : True, 'url-redirected': urlRedirect, 'verb': 'unknow', 'noun': 'unknow' }
    # insert
    es.index(index=IDXPROJ, doc_type=DOCTYPE, id='redirected'+str(self.linkID), body=inputLink)
    self.linkID += 1

  ###############################################################
  # Method for extract redirected links
  ###############################################################
  def findRedirects(self,es):
    pageTitle = ""

    #file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/Wikilinks/redirectedLinks.redirect','w+')
    print 'Začíná parsing...'
    # parsování data
    for event, elem in ET.iterparse('/mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/enwiki-20160407-pages-articles.xml'):
      if event == 'end':
        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
          pageTitle = unicode(elem.text).encode('utf-8')
        elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}redirect":
          pageRedirect = unicode(elem.attrib['title'].replace(' ','_')).encode('utf-8')
          #file.write('https://en.wikipedia.org/wiki/'+pageTitle.replace(' ','_')+'\thttps://en.wikipedia.org/wiki/'+pageRedirect+'\n')
          # elastic insert
          self.insertWikilinks('https://en.wikipedia.org/wiki/'+pageTitle.replace(' ','_'), 'https://en.wikipedia.org/wiki/'+pageRedirect, es)
      elem.clear()  # discard the element

    file.close()

# main
if __name__ == "__main__":
  # nastavení databáze elastic search
  HOST        = 'athena1.fit.vutbr.cz'
  PORT        = 9200
  DOCTYPE     = 'wikilinks'
  IDXPROJ     = 'xstejs24_extractor'

  insertRedirect = InsertRedirect()

  # DB connect
  es = Elasticsearch(host=HOST, port=PORT)
  # parsování
  insertRedirect.findRedirects(es)

  print "Done"

  sys.exit(0)
