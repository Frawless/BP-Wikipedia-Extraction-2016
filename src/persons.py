#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import re

###############################################################
# ???
###############################################################
def getEntityInfo(sentence):
  verb = ""
  noun = ""
  #print sentence
  # TODO - for humanoid entities is tmpVerb regex enought, but if you wanna check all type of entities is more better here
  # TODO - loop over sentence and create expresion 'what is current entity' like in find.py - method checkInformation() line 14
  tmpVerb = re.search('\[\[([^\|]+)\|V[^\|]+\|be\]\].*?\[\[([^\|]+)\|N[N|P]\|[^\]]+\]\][^\n]+', sentence)
  #tmpNoun = re.search('\[\[([^\|]+)\|V[^\|]+\|be\]\].*?\[\[([^\|]+)\|N[^\]]+\]\] \[\[([^\|]+)\|N[^\]]+\]\][^\n]+',sentence)
  if tmpVerb:
    verb = tmpVerb.group(1)
    noun = tmpVerb.group(2)

  #print verb+" "+noun
  if verb == "":
    verb = "uknown"
  if noun == "":
    noun = "uknown"
  return verb, noun

###############################################################
# Method for extract persons from current page
# TODO - lehce rozdělit, zpřeheldnit, vylepšit tuto metodu
###############################################################
def getPersons(page, listOfNouns, wikiLinksFile):
  names = []
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
        wikiLinksFile.write(url.group(1)+'\t')
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
        verb, noun = getEntityInfo(sentence)
        wikiLinksFile.write(verb+' '+noun+'\n')
        writeFirstSentence = False
      # parse only sentences with verb (VERB FILTER)
      if not re.search('\[([^\|]+\|V[^\|]+\|[^\]]+)\]',sentence):
        continue
      for item in sentence.split(" "):
        # print item
        isName = re.search(r'\[\[[^\|]+\|([^\|]+)', item)
        if isName:
          if isName.group(1) == "NP" or isName.group(1) == "GGG" or isName.group(1) == "POS" or isName.group(1) == "IN" and nextName:
            if isName.group(1) == "POS":
              parsedName = ""
              nextName = False
              continue
            # print "tvořím jméno"
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
                #print "neparsuju"
              parsedName = re.sub(r'\|[^\]]+\]\]', '', parsedName).replace('[[', '')
              #parsedName = parsedName;
              # print "parsed name obsahuje NP"
            else:
              parsedName = ""
              continue
            if set:
              for part in parsedName.split(" "):
                # print "part výpis pro porování se seznamem"
                # print part
                if part.lower() in listOfNouns:
                #if re.sub(r'\|[^\]]+\]\]', '', part).replace('[[', '').lower() in listOfNouns:
                  # print part+" -> je součástí listu"
                  parsedName = ""
                  realName = ""
                  break
                if part in parsedName and part not in realName:
                  #if "." not in part:
                  realName += part + " "

              if realName is not "" and compareNames(realName,names):
                output += realName[:-1] + "\t" + pageURL + "\t" + re.sub(r'\|[^\]]+\]\]', '',sentence).replace('[[', '') + "\n"
                # zakomentováno -> odstranění duplicit
                #names.append(real_name[:-1])
                realName = ""
                parsedName = ""
                URL = ""
                set = False
              else:
                realName = ""
  # return output -> maybe output[:-1] but in this case some entities are grouped together
  return output

###############################################################
# Method for compare entity name with entities with URL from current page
###############################################################
def compareNames(name, name_array):
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
