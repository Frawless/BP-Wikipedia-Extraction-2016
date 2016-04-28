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

###############################################################
# Method for Elastic insert Wikilinks
###############################################################
def insertWikilinks(url, urlRedirect):
  # nastavení databáze elastic search
  HOST        = 'athena1.fit.vutbr.cz'
  PORT        = 9200
  DOCTYPE     = 'wikilinks'
  IDXPROJ     = 'xstejs24_extractor'

  # DB connect
  es = Elasticsearch(host=HOST, port=PORT)

  # new input
  inputLink = {'url': url, 'redirect' : True, 'url-redirected': urlRedirect, 'verb': 'unknow', 'noun': 'unknow' }
  # insert
  es.index(index=IDXPROJ, doc_type=DOCTYPE, body=inputLink)

# FUNKCE parseOut
# funkce pro zpracování výstupu dotazovače pomocí regexu
# @param result - výstup z dotazovače
# @return out - výstupní zpracovaný text
def findRedirects():
  pageTitle = ""

  file = open('/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/redirectedLinks.redirect','w+')
  print 'Začíná parsing...'
  # parsování data
  for event, elem in ET.iterparse('/mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/enwiki-20160113-pages-articles.xml'):
    if event == 'end':
      if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
        pageTitle = unicode(elem.text).encode('utf-8')
      elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}redirect":
        pageRedirect = unicode(elem.attrib['title'].replace(' ','_')).encode('utf-8')
        #file.write('https://en.wikipedia.org/wiki/'+pageTitle.replace(' ','_')+'\thttps://en.wikipedia.org/wiki/'+pageRedirect+'\n')
        # elastic insert
        insertWikilinks('https://en.wikipedia.org/wiki/'+pageTitle.replace(' ','_'), 'https://en.wikipedia.org/wiki/'+pageRedirect)
    elem.clear()  # discard the element

  file.close()

# main
if __name__ == "__main__":
  # parsování
  findRedirects()

  print "Done"

  sys.exit(0)
