#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import re
import sys
import socket
import json
import time

###############################################################
# Class for persone xtract
###############################################################
class PersonClass:
  ###############################################################
  # Class init
  ###############################################################
  def __init__(self, wikiLinks, listOfNouns):
      self.wikiLinks = wikiLinks
      self.listOfNouns = listOfNouns
  ###############################################################
  # Method for parse basic information about entity from article
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
      output += key+'\t'+found[key]+'\n'
    # return statement
    return output

  ###############################################################
  # Method for extract persons from current page
  ###############################################################
  def getPersons(self,page, extractorClass):
    names = []
    link = ""
    output = ""
    realName = ""
    parsedName = ""
    pageURL = ""
    set = False
    nextName = True
    writeFirstSentence = False

    #final output
    finalOutput = ""

    for sentence in page.split("\n"):
      # parsing sentence with PAGE tag (PAGE FILTER)
      if "%%#PAGE" in sentence:
        url = re.search('%%#PAGE.*\t(http[^\s]+)',sentence)
        if url:
          link = url.group(1)
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
          self.wikiLinks.write(link+'\t'+verb+' '+noun+'\n')
          extractorClass.articlesCount += 1
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
                if not '.' in item and len(item) < 2:
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
              if parsedName.count('NP') > 1 and re.search('\s', parsedName[:-1]) and not re.search('\d',parsedName):
                if (len(re.findall('[A-Z][a-z]+', parsedName)) >= 1 and len(re.findall('\s',parsedName[:-1])) == 0) or (len(re.findall('[A-Z][a-z]+', parsedName)) > 1 and len(re.findall('\s',parsedName[:-1])) > 0):
                  if "URL=" in parsedName:
                    nextName = True
                    names.append(re.sub(r'\|[^\]]+\]\]', '', parsedName).replace('[[', ''))
                    parsedName = ""
                    continue
                  parsedName = re.sub(r'\|[^\]]+\]\]', '', parsedName).replace('[[', '')
                else:
                  parsedName = ""
                  continue
              else:
                parsedName = ""
                continue
              if set and parsedName is not "":
                for part in parsedName.split(" "):
                  if part.lower() in self.listOfNouns:
                    parsedName = ""
                    realName = ""
                    break
                  if part in parsedName and part not in realName:
                    #if "." not in part:
                    if re.search('minister|president|colonel|lieutenant|major|officer|corporal|sergeant|master|commander|admiral|apprentice|chiev|manager|governor',part,re.IGNORECASE):
                      realName = ""
                      continue
                    if re.search('\s+.',part):
                      continue
                    realName += part + " "

                if realName is not "" and self.compareNames(realName,names) and self.excludeEntityKind(realName):
                  #output += realName[:-1] + "\t" + pageURL + "\t" + re.sub(r'\|[^\]]+\]\]', '',sentence).replace('[[', '') + "\n"
                  # test pro věty s anotacemi
                  output += realName[:-1] + "\t" + pageURL + "\t" + sentence + "\t"+noun+"\n"
                  realName = ""
                  parsedName = ""
                  set = False
                else:
                  realName = ""

    # odstranění entity, které jsou referencovány na konci
    for line in output.split('\n'):
      entity = re.search('[^\t]+\thttp[^\n]+\n',line)
      if entity not in names:
        finalOutput += line+'\n'
        extractorClass.extractedEntityCount += 1

    # return output -> maybe output[:-1] but in this case some entities are grouped together
    return self.deleteDuplicity(finalOutput)

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

  ###############################################################
  # Method for exclude possesive entity
  ###############################################################
  def excludeEntityKind(self,realName):
    for item in realName.split(' '):
      if re.search('nal|ral|tal|cal|ish|can|ian|lic|fic|tic|pic|mic|gic|ing',item[-3:]):
        return False
    return True
