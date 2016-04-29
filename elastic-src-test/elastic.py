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
      'extracted': {
          'properties': {
              'id':               {'type':'string'},
              'host':             {'type':'string'},
              'entity':           {'type':'string'},
              'url':              {'type':'string' },
              'sentences': {
                'type': 'nested',
                'include_in_parent': True,
                'properties': {
                  'appereance':		   { 'type': 'string' }
                }
              },
          }
      },
      'withoutURL': {
          'properties': {
              'id':               {'type':'long'},
              'host':           {'type':'string'},
              'entity':       {'type':'string'},
              'url':    {'type':'string' },
              'sentences': {
                'type': 'nested',
                'include_in_parent': True,
                'properties': {
                  'appereance':		   { 'type': 'string' }
                }
              },
          }
      },
      'checkedURL': {
          'properties': {
              'id':               {'type':'long'},
              'host':           {'type':'string'},
              'entity':       {'type':'string'},
              'url':    {'type':'string' },
              'sentences': {
                'type': 'nested',
                'include_in_parent': True,
                'properties': {
                  'appereance':		   { 'type': 'string' }
                }
              },
          }
      },
      'alreadyURL': {
          'properties': {
              'id':               {'type':'long'},
              'host':           {'type':'string'},
              'entity':       {'type':'string'},
              'url':    {'type':'string' },
              'sentences': {
                'type': 'nested',
                'include_in_parent': True,
                'properties': {
                  'appereance':		   { 'type': 'string' }
                }
              },
          }
      }
  }

  # smazání DB
  #es.indices.delete(index='xstejs24_extractor')
  #sys.exit(0)

  # create DB - jendou odkomenovat a pak už mít zakomenované při opakovaném spouštění
  #es.indices.create(index='xstejs24_extractor',    body={'mappings': proj_mapping  })

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
                  { "match": { "url":   "https://en.wikipedia.org/wiki/Manchester_Eagles"}},
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
  # Method for Elastic insert entity
  ###############################################################
  def insertEntity(self,entity, url, sentences):
    appereance = '['
    # nastavení databáze elastic search
    HOST        = 'athena1.fit.vutbr.cz'
    PORT        = 9200
    DOCTYPE     = 'extracted'
    IDXPROJ     = 'xstejs24_extractor'

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
    self.entityID += 1


###############################################################
# Main
###############################################################
if __name__ == "__main__":
  createDB()
  print "Tradá!"
  sys.exit(0)

#curl -XGET 'http://localhost:9200/xstejs24_extractor/wikilinks/_count?pretty=true'
#curl -XGET 'http://localhost:9200/xstejs24_extractor/wikilinks/[ID]?pretty=true'
