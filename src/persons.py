#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import re

def getPersons(page, listOfNouns):
  names = []
  output = ""
  real_name = ""
  parsed_name = ""
  URL = ""
  page_URL = ""
  set = False
  next_name = True
  # print page.replace('\n','@\n')
  # print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  for sentence in page.split("\n"):
    # print sentence
    if "%%#PAGE" in sentence:
    # print "parse page"
    # print sentence
      if "entity=" in sentence:
        entity = re.search(r'[^ ]+ ([^\t]+)\t(http[^\s]+)\sentity=([^\s]+)', sentence)
        #page_URL = entity.group(2)
      else:
        entity = re.search(r'[^ ]+ ([^\t]+)\t(http[^\s]+)', sentence)
      if entity:
        # print entity.group(1)
        page_URL = entity.group(2)
        # print page_URL
        real_name += entity.group(1) + "|" + entity.group(2)
        names.append(entity.group(1))
        # print "přidání do names při page"
        # print real_name
        names.append(real_name)
        real_name = ""
    else:
      # print "parse non.page"
      # print sentence
      for item in sentence.split(" "):
        # print item
        isName = re.search(r'\[\[[^\|]+\|([^\|]+)', item)
        if isName:
          if isName.group(1) == "NP" or isName.group(1) == "GGG" or isName.group(1) == "POS" or isName.group(1) == "IN" and next_name:
            if isName.group(1) == "POS":
              parsed_name = ""
              next_name = False
              continue
            # print "tvořím jméno"
            tmp = re.search(r'\[\[([^\|]+)', item)
            if tmp:
              if tmp.group(1) is not "of" and isName.group(1) == "IN":
                parsed_name = ""
                next_name = False
                continue
              parsed_name += item + " "
              set = True
            '''if "URL=" in item:
              tmp = re.search(r'\|URL=([^\]]+)', item)
              parsed_name = ""
              next_name = False
              continue'''
            if "entity=" in item:
              entity = re.search(r'\|entity=(person|artist)', item)
              if not entity:
                parsed_name = ""
                next_name = False
                continue
          else:
            next_name = True
            if parsed_name.count('NP') > 1 and re.search('\s', parsed_name[:-1]) and not re.search('\d',parsed_name) and len(re.findall('[A-Z]', parsed_name)) > 1:
              # print re.search('\s',parsed_name)
              if "URL=" in parsed_name:
                next_name = True
                names.append(re.sub(r'\|[^\]]+\]\]', '', parsed_name).replace('[[', ''))
                parsed_name = ""
                continue
                #print "neparsuju"
              parsed_name = re.sub(r'\|[^\]]+\]\]', '', parsed_name).replace('[[', '')
              #parsed_name = parsed_name;
              # print "parsed name obsahuje NP"
              # print parsed_name
            else:
              parsed_name = ""
              continue
            if set:
              for part in parsed_name.split(" "):
                # print "part výpis pro porování se seznamem"
                # print part
                if part.lower() in listOfNouns:
                #if re.sub(r'\|[^\]]+\]\]', '', part).replace('[[', '').lower() in listOfNouns:
                  # print part+" -> je součástí listu"
                  parsed_name = ""
                  real_name = ""
                  break
                if part in parsed_name and part not in real_name:
                  if "." not in part:
                    real_name += part + " "
              if real_name is not "" and compareNames(real_name,names) and URL is "":
              #if real_name is not "" and real_name[:-1] not in names and URL is "":
                # print "Přidávám: "+real_name
                output += real_name + "\t" + page_URL + "\t" + re.sub(r'\|[^\]]+\]\]', '',sentence).replace('[[', '') + "\n"
                # zakomentováno -> odstranění duplicit
                #names.append(real_name[:-1])
                real_name = ""
                parsed_name = ""
                URL = ""
                set = False

  return output[:-1]


def compareNames(name, name_array):
  #print name_array
  heurestic = 0
  #print name
  if name in name_array:
    return False
  # get single name from list
  for item in name_array:
    #name = name.split(" ")  # split name to single words
    item = item.split(" ")  # split name from lsit to single words
    # iterating of single words
    for part in item:
      for part2 in name:
        if part == part2:
          heurestic += 1
    if heurestic > 1:
      return False
  return True
