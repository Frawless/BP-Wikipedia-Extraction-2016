#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import json
# knihovna
from elasticsearch import Elasticsearch

def createDB():
  # nastavení databáze elastic search
  HOST        = 'athena1.fit.vutbr.cz'
  PORT        = 9200
  DOCTYPE     = 'wikilinks'
  IDXPROJ     = 'xstejs24_extractor'

  # DB conects
  es = Elasticsearch(host=HOST, port=PORT)

  # DB definition
  proj_settings = {
      'analysis': {
          'analyzer': {
              'analyzer_keyword': {
                  'tokenizer': 'keyword',
                  'filter': 'lowercase'
              }
          }
      }
  }
  # DB mapping
  proj_mapping = {
      'wikilinks': {
          'properties': {
              'id':             {'type':'string','index': 'not_analyzed'},
              'url':            {'type':'string','index': 'not_analyzed'},
              'redirect':       {'type':'boolean','index': 'not_analyzed'},
              'url-redirected': {'type':'string','index': 'not_analyzed'},
              'verb':           {'type':'string','index': 'not_analyzed'},
              'noun':           {'type':'string','index': 'not_analyzed'},
          }
      },
      'statistic': {
          'properties': {
              'id':             {'type':'string','index': 'not_analyzed'},
              'host':           {'type':'string','index': 'not_analyzed'},
              'time':           {'type':'string','index': 'not_analyzed'},
              'articles':       {'type':'string','index': 'not_analyzed'},
              'entity':         {'type':'string','index': 'not_analyzed'},
          }
      },
      'extracted': {
          'properties': {
              'id':               {'type':'string','index': 'not_analyzed'},
              'entity':           {'type':'string','index': 'not_analyzed'},
              'page':             {'type':'string','index': 'not_analyzed'},
              'info':             {'type':'string','index': 'not_analyzed'},
          }
      }
  }

  # DB delete
  #es.indices.delete(index='xstejs24_extractor')
  #sys.exit(0)
  #print 'Smazáno'

  # create DB
  #es.indices.create(index='xstejs24_extractor',    body={'mappings': proj_mapping  })
  #sys.exit(0)

  # new input
  delivData = {'id': '22', 'host': 'athena1', 'entity' : 'Donald J. Hornster', 'url': 'http-wiki', }
  nestedData = {'flags' : [{'sentence': "anotovana veta 2"}, {'sentence': "anotovana veta 1"}]}
  # normalni insert
  #es.index(index=IDXPROJ, doc_type=DOCTYPE, id = 1,body=delivData) # pokud id nezadano, automaticky vygenerovano

  # nested update
  #es.update(index=IDXPROJ, doc_type=DOCTYPE, id=1, body={'doc': nestedData}) # pokud id nezadano, automaticky vygenerovano

  # entity update
  #es.update(index=IDXPROJ, doc_type=DOCTYPE, id=1, body={'doc': projectData}) # dle ID jedině, ne dotazem pro vícero (deprecated)

  # získání dle ID konkrétního jednoho
  #print es.get(index=IDXPROJ, doc_type=DOCTYPE, id=1) # pokud znáš ID, jinak vyhledáváš (id zde a v JSONu není to samé místo v paměti)

  # vyhleádní - stačí pro získání všech záznamů
  qbody = {
        "version": 'true',
        "query": {
          "bool": {
            "must": [
              { "match": { "host":'athena1'}},
            ],

          }
      }}

  # vyhleádní - s filtrem
  '''qbody = {
        "query": {
          "filtered": {
            "query" :{
              "bool": {
                "must": [
                  { "match": { "url":   "https://en.wikipedia.org/wiki/Spanish Empire"}},
                ],
              }
            },
            "filter":{
              "term":  { "host": "athena1" }

            }
          }
      }}'''


  jsonTest = es.search(index=IDXPROJ, doc_type=DOCTYPE, body=qbody)
  print jsonTest

  '''for item in jsonTest['hits']['hits']:
    print item.get('_source').get('entity')
    for tmp in item.get('_source').get('flags'):
      print item.get('_source').get('flags')'''

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  createDB()
  print "Tradá!"
  sys.exit(0)

#curl -XGET 'http://localhost:9200/xstejs24_extractor/wikilinks/_count?pretty=true'
#curl -XGET 'http://localhost:9200/xstejs24_extractor/wikilinks/[ID]?pretty=true'
