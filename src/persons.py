#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import re
import sys
import socket
import json
import time
from elasticsearch import Elasticsearch


class PersonClass:
  # init
  def __init__(self, entityID,linkID):
      self.entityID = entityID
      self.linkID = linkID
  ###############################################################
  # ???
  ###############################################################
  def getEntityInfo(self,sentence):
    verb = ""
    noun = ""
    findNoun = False
    #print sentence
    # TODO - for humanoid entities is tmpVerb regex enought, but if you wanna check all type of entities is more better here
    # TODO - loop over sentence and create expresion 'what is current entity' like in find.py - method checkInformation() line 14
    tmpVerb = re.search('\[\[([^\|]+)\|V[^\|]+\|be\]\].*?\[\[([^\|]+)\|N[N]\|[^\]]+\]\][^\n]+', sentence)
    #tmpNoun = re.search('\[\[([^\|]+)\|V[^\|]+\|be\]\].*?\[\[([^\|]+)\|N[^\]]+\]\] \[\[([^\|]+)\|N[^\]]+\]\][^\n]+',sentence)
    if tmpVerb:
      verb = tmpVerb.group(1)
      noun = tmpVerb.group(2)

    for token in sentence.split(' '):
      if findNoun:
        tmpNoun = re.search('\[\[([^\|]+)\|N[N]\|[^\]]+\]\]',token)
        if tmpNoun:
          noun += ' '+tmpNoun.group(1)
        else:
          break;
      if noun in token:
        findNoun = True


    #print verb+" "+noun
    if verb == "":
      verb = "uknown"
    if noun == "":
      noun = "uknown"
    return verb, noun

  ###############################################################
  # Method for delete duplicity
  ###############################################################
  def deleteDuplicity(self,entity):
    output = ""
    found = {}
    #loop over all found entity
    for line in entity.split('\n'):
      item = re.search('([^\t]+)\t([^\t]+)\t([^\n]+)',line)
      if not item:
        continue
      if item.group(1) in found:
        found[item.group(1)] += '|'+item.group(3)
      else:
        found[item.group(1)] = item.group(2)+'\t'+item.group(3)

    for key in found:
      url = re.search('([^\t]+)\t([^\n]+)',found[key])
      self.insertEntity(key,url.group(1),url.group(2))
      output += key+'\t'+found[key]+'\n'

  ###############################################################
  # Method for Elastic insert Wikilinks
  ###############################################################
  def insertWikilinks(self,link):
    # nastavení databáze elastic search
    HOST        = 'athena1.fit.vutbr.cz'
    PORT        = 9200
    DOCTYPE     = 'wikilinks'
    IDXPROJ     = 'xstejs24_extractor'

    # DB connect
    es = Elasticsearch(host=HOST, port=PORT)

    # new input
    inputLink = {'id': socket.gethostname()+'-'+str(self.linkID),'url': link[0], 'redirect' : False, 'url-redirected': 'none', 'verb': link[1], 'noun': link[2] }
    # insert
    es.index(index=IDXPROJ, doc_type=DOCTYPE, id=socket.gethostname()+'-'+str(self.linkID), body=inputLink)
    self.linkID += 1
    if self.linkID % 15000 == 0:
      print "Šlofík..."
      time.sleep(60)

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
  # Method for extract persons from current page
  # TODO - lehce rozdělit, zpřeheldnit, vylepšit tuto metodu
  ###############################################################
  def getPersons(self,page, listOfNouns, wikiLinksFile):
    names = []
    link = []
    output = ""
    realName = ""
    parsedName = ""
    pageURL = ""
    set = False
    nextName = True
    writeFirstSentence = False

    for sentence in page.split("\n"):
      # parsing sentence with PAGE tag (PAGE FILTER)
      if "%%#PAGE" in sentence:
        url = re.search('%%#PAGE.*\t(http[^\s]+)',sentence)
        if url:
          link.append(url.group(1))
          #wikiLinksFile.write(url.group(1)+'\t')
          writeFirstSentence = True
        if "entity=" in sentence:
          entity = re.search(r'[^ ]+ ([^\t]+)\t(http[^\s]+)\sentity=([^\s]+)', sentence)
        else:
          entity = re.search(r'[^ ]+ ([^\t]+)\t(http[^\s]+)', sentence)
        if entity:
          pageURL = entity.group(2)  # save actual page URL
          realName += entity.group(1) + "|" + entity.group(2)  # actual page entity + URL
          names.append(entity.group(1))
          names.append(realName)
          realName = ""
      else:
        # add first sentence from page to list for checking entities url
        if writeFirstSentence:
          verb, noun = self.getEntityInfo(sentence)
          #wikiLinksFile.write(verb+' '+noun+'\n')
          link.append(verb)
          link.append(noun)
          self.insertWikilinks(link)
          #link[1], link[2] = getEntityInfo(sentence)
          writeFirstSentence = False
        # parse only sentences with verb (VERB FILTER)
        if not re.search('\[([^\|]+\|V[^\|]+\|[^\]]+)\]',sentence):
          continue
        for item in sentence.split(" "):
          isName = re.search(r'\[\[[^\|]+\|([^\|]+)', item)
          if isName:
            if isName.group(1) == "NP" or isName.group(1) == "GGG" or isName.group(1) == "POS" or isName.group(1) == "IN" and nextName:
              if isName.group(1) == "POS":
                parsedName = ""
                nextName = False
                continue
              tmp = re.search(r'\[\[([^\|]+)', item)
              if tmp:
                if tmp.group(1) is not "of" and isName.group(1) == "IN":
                  parsedName = ""
                  nextName = False
                  continue
                parsedName += item + " "
                set = True

              if "entity=" in item:
                entity = re.search(r'\|entity=(person|artist)', item)
                if not entity:
                  parsedName = ""
                  nextName = False
                  continue
            else:
              nextName = True
              if parsedName.count('NP') > 1 and re.search('\s', parsedName[:-1]) and not re.search('\d',parsedName) and len(re.findall('[A-Z][a-z]+', parsedName)) > 1:
                if "URL=" in parsedName:
                  nextName = True
                  names.append(re.sub(r'\|[^\]]+\]\]', '', parsedName).replace('[[', ''))
                  parsedName = ""
                  continue
                parsedName = re.sub(r'\|[^\]]+\]\]', '', parsedName).replace('[[', '')
              else:
                parsedName = ""
                continue
              if set:
                for part in parsedName.split(" "):
                  if part.lower() in listOfNouns:
                    parsedName = ""
                    realName = ""
                    break
                  if part in parsedName and part not in realName:
                    #if "." not in part:
                    realName += part + " "

                if realName is not "" and self.compareNames(realName,names):
                  output += realName[:-1] + "\t" + pageURL + "\t" + re.sub(r'\|[^\]]+\]\]', '',sentence).replace('[[', '') + "\n"
                  realName = ""
                  parsedName = ""
                  set = False
                else:
                  realName = ""
    # return output -> maybe output[:-1] but in this case some entities are grouped together
    self.deleteDuplicity(output)
    return self.entityID, self.linkID

  ###############################################################
  # Method for compare entity name with entities with URL from current page
  ###############################################################
  def compareNames(self,name, name_array):
    heurestic = 0
    if name in name_array:
      return False
    # get single name from list
    for item in name_array:
      # iterate over names in array and compare with entity name
      for part in name.split(" "):
        if part == "":
          continue
        if part in item:
          heurestic += 1
      if heurestic > 1:
        return False
      else:
        heurestic = 0
    return True
