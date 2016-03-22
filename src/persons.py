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
        page_URL = entity.group(2)
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
          if isName.group(1) == "NP" or isName.group(1) == "NN" or isName.group(1) == "GGG" or isName.group(1) == "POS" and next_name:
            if isName.group(1) == "POS":
              parsed_name = ""
              next_name = False
              continue
            # print "tvořím jméno"
            tmp = re.search(r'\[\[([^\|]+)', item)
            if tmp:
              parsed_name += item + " "
              set = True
            if "URL=" in item:
              tmp = re.search(r'\|URL=([^\]]+)', item)
              parsed_name = ""
              next_name = False
              continue
            if "entity=" in item:
              entity = re.search(r'\|entity=(person|artist)', item)
              if not entity:
                parsed_name = ""
                next_name = False
                continue
        else:
          next_name = True
          # print "parsed name před ověřením"
          # print parsed_name
          if parsed_name.count('NP') > 1 and re.search('\s', parsed_name[:-1]) and not re.search('\d',parsed_name) and len(re.findall('[A-Z]', parsed_name)) > 1:
            # print re.search('\s',parsed_name)
            parsed_name = re.sub(r'\|[^\]]+\]\]', '', parsed_name).replace('[[', '')
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
                # print part+" -> je součástí listu"
                parsed_name = ""
                real_name = ""
                break
              if part in parsed_name and part not in real_name:
                if "." not in part:
                  real_name += part + " "

            '''print "names"
            print names
            print "real name"
            print real_name'''
            # print "output"
            # print output
            if real_name is not "" and real_name[:-1] not in names and URL is "":
              # print "Přidávám: "+real_name
              output += real_name + "\t" + page_URL + "\t" + re.sub(r'\|[^\]]+\]\]', '',sentence).replace('[[', '') + "\n"
              # print "přidání do names"
              # print real_name[:-1]
              # zakomentováno -> odstranění duplicit
              #names.append(real_name[:-1])
              real_name = ""
              parsed_name = ""
              URL = ""
              # print name.replace('\n','') + "-> "+re.sub(r'\|[^\]]+\]\]','',sentence).replace('[[','').replace('\n','')+"\n"

              name = ""
              # print output
              set = False
              # print "Výsledek funkce getPersons()"
              # print "names:"
              # print names
              # print "output:"
              # print output[:-2]
  return output[:-2]

