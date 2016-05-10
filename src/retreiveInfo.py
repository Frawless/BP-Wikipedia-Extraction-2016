#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz

import sys
import re

###############################################################
# Constants
###############################################################
PathPrefix = '/mnt/minerva1/nlp/projects/ie_from_wikipedia7/servers_output/'

def getInfo(sentences,entity,url):
  subjectsList = []
  entityHighLetters = len(re.findall('[A-Z][a-z]+',entity))


  for item in entity.split(' '):
    subjectsList.append(item)

  # split sentences
  for sentence in sentences.split(' |'):
    predicate = ''
    subject = ''
    nextSubject = True
    gotPredicate = False
    writeData = False
    context = ''
    subjectsList = []
    predicatesList = []
    info = []
    # split sentence into tokens
    print entity
    sentenceData = re.search('(.*)(\[\['+entity.replace(' ','.*')+'.*\]\])([^\n]+)',sentence)
    # ....
    if sentenceData:
      print sentence
      # procházení tokenů ve větách
      for token in sentence.split(' '):
        # hledání podmětu
        #print token
        tokenData = re.search('(\[\[([^\|]+)\|([^\|]+)\|([^\]]+)\]\])',token)
        if tokenData:
          #print previousTag
          if (re.search('^[NJ].*',tokenData.group(3)) or re.search('POS',tokenData.group(4)) or re.search('CC',tokenData.group(3))) and nextSubject:
            subject += token+' '
            print subject
            #print subject
            subjectsList.append(tokenData.group(2))
          elif re.search('^V.*',tokenData.group(3)) and subject is not '' and not gotPredicate:
            predicate += token+' '
            nextSubject = False
          elif re.search('\.|\,', tokenData.group(4)) or writeData:
            print 'hu'+subject
            # pokud je inforamce již v subjectu -> team maanger + entity
            if len(re.findall(' ',subject[:-1])) > len(re.findall(' ',entity)) and re.search(entity.replace('','.*')+'.*',subject):
              if (len(re.findall('NP',subject[:-1])) - entityHighLetters) < entityHighLetters:
                print 'Test: '+subject+' '+predicate+' '+context
                info.append(entity+' was '+re.sub('\[\['+entity.replace(' ','.*')+'.*','',subject[:-1])+'of '+url)
            print 'Test: '+subject+' '+predicate+' '+context
            if subject is not '' and gotPredicate and re.search(entity.replace('','.*')+'.*',subject+' '+context):
              info.append(subject+predicate+context[:-1])
            subject = ''
            predicate = ''
            context = ''
            gotPredicate = False
            nextSubject = True
            writeData = False
          elif predicate is not '' and subject is not '':
            context += token+' '
            gotPredicate = True
          else:
            print 'ha'+subject
            if len(re.findall(' ',subject[:-1])) > len(re.findall(' ',entity)) and re.search(entity.replace('','.*')+'.*',subject):
              if (len(re.findall('NP',subject[:-1])) - entityHighLetters) < entityHighLetters:
                print 'Test: '+subject+' '+predicate+' '+context
                info.append(entity+' was '+re.sub('\[\['+entity.replace(' ','.*')+'.*','',subject[:-1])+'of '+url)
            subject = ''
            predicate = ''
            context = ''
            gotPredicate = False
            nextSubject = True

    # úprava výsledků
    for data in info:
      output = ''
      #print 'Nález před: '+data
      for token in data.split(' '):
        if token in url and len(token) > 3:
          token = url
        output += re.sub('\|[^\]]+\]\]','',token.replace('[[',''))+' '
      print 'Nález po: '+output[:-1]
      #print 'Nález: '+data
      #data = 'Entita: '+entity+' Predicate: '+predicate[:-1]+' Subject: '+subject[:-1]+' Time: '+time
      #print data


###############################################################
# Main
###############################################################
if __name__ == "__main__":
  endCnt = 0
  with open(PathPrefix+'backup-extract/entity-non-page.checked','r') as inputFile:
    for line in inputFile:
      endCnt += 1

      data = re.search('([^\t]+)\t([^\t]+)\t([^\n]+)\n', line)
      if data:
        entity = data.group(1)
        url = data.group(2)
        sentences = data.group(3)
        getInfo(sentences,entity,url)
      if endCnt > 25:
        print "Test hotov"
        sys.exit(0)

  sys.exit(0)