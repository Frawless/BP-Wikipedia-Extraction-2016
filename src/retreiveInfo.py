
#!/usr/bin/python
# coding: UTF-8
# -*-: coding: utf-8 -*-
# autor: Jakub Stejskal, xstejs24@stud.fit.vutbr.cz
import os
import sys
import re
import socket

###############################################################
# Constants
###############################################################
PathPrefix = sys.argv[1]

###############################################################
# Method for extract information about extracted entity
###############################################################
def getInfo(sentences,entity,url,interest):
  entityHighLetters = len(re.findall('[A-Z][a-z]+',entity))
  output = ''
  # Loop over extracted sentences
  for sentence in sentences.split(' |'):
    predicate = ''
    subject = ''
    nextSubject = True
    gotPredicate = False
    writeData = False
    context = ''
    info = []


    # Split sentence into tokens
    for token in sentence.split(' '):
      # Find data inside token
      tokenData = re.search('(\[\[([^\|]+)\|([^\|]+)\|([^\]]+)\]\])',token)
      if tokenData:
        # Token is subject
        if (re.search('^[NJ].*|CC|:',tokenData.group(3)) or re.search('POS',tokenData.group(4)) or re.search('CC',tokenData.group(3))) and nextSubject:
          subject += token+' '
        # Token is predicate
        elif re.search('^V.*',tokenData.group(3)) and subject is not '' and not gotPredicate:
          predicate += token+' '
          nextSubject = False
        # Token is end-of-senntence
        elif re.search('\.|\,', tokenData.group(4)) or writeData:
          tmpSubject = re.sub('\|[^\]]+\]\]','',subject[:-1]).replace('[[','')
          # Check if only sentence subject and entity is in subject, no predicate needed
          if len(re.findall(' ',subject[:-1])) > len(re.findall(' ',entity)) and entity in tmpSubject:
            if (len(re.findall('NP',subject[:-1])) - entityHighLetters) < entityHighLetters:
              # Remove every spare text
              subject = tmpSubject

              if re.match(re.escape(entity),subject):
                subject = subject.replace(entity+' ','')
              # Subject must have few words after entity replace
              if subject is not '':
                # Present time
                if re.search('former|actual|is|current',subject, re.IGNORECASE):
                  info.append('Entity:'+entity.replace(' ','_')+' is '+subject+' of '+url)   # Create information
                # Previous time
                else:
                  info.append('Entity:'+entity.replace(' ','_')+' was '+subject+' of '+url)  # Create information
          # False information
          #createInformation(subject, entity, url, info,entityHighLetters)
          # Check if system found all data for create structured info
          if subject is not '' and gotPredicate and entity in tmpSubject:
            subject = tmpSubject
            if re.match(re.escape(entity),subject):
              subject = ' '+subject.replace(entity,'')
            if re.search('[A-Z]*|[a-z]*',subject):
              subject = ''
            info.append('Entity:'+entity.replace(' ','_')+subject+' '+predicate+context[:-1]) # Create information
          # Clear variables
          subject = ''
          predicate = ''
          context = ''
          gotPredicate = False
          nextSubject = True
          writeData = False
        # Token is another kind of word, have predicate and subject, create info context
        elif predicate is not '' and subject is not '':
          if 'POS' in token:
            context = context[:-1]+token+' '
          else:
            context += token+' '
          gotPredicate = True
        else:
          createInformation(subject, entity, url, info,entityHighLetters)
          # Clear variables
          subject = ''
          predicate = ''
          context = ''
          gotPredicate = False
          nextSubject = True
    # Check data after sentence and create info
    if predicate is not '' and subject is not '' and context is not '':
      info.append('Entity:'+entity.replace(' ','_')+' '+predicate+context)  # Create information

    # Replace token follow on URL by URL
    for data in info:
      for token in data.split(' '):
        token = re.sub('\|[^\]]+\]\]','',token.replace('[[',''))
        if token in url and len(token) > 3:
          token = url
        output += token+' '
      output += '\tPAGE: '+url+'\n'

  # Return
  #print output[:-1]
  return output[:-1]


###############################################################
# Method for create info
###############################################################
def createInformation(subject, entity, url, info,entityHighLetters):
  tmpSubject = re.sub('\|[^\]]+\]\]','',subject[:-1]).replace('[[','')
  # Check if only sentence subject and entity is in subject, no predicate needed
  #if len(re.findall(' ',subject[:-1])) > len(re.findall(' ',entity)) and re.search(entity.replace('','.*')+'.*',subject):
  if len(re.findall(' ',subject[:-1])) > len(re.findall(' ',entity)) and entity in tmpSubject:
    if (len(re.findall('NP',subject[:-1])) - entityHighLetters) < entityHighLetters:
      # Remove every spare text
      #subject = re.sub('\[\['+entity.replace(' ','.*')+'.*','',subject[:-1])
      subject = tmpSubject
      if re.match(re.escape(entity),subject):
        subject = subject.replace(entity+' ','')
      # Subject must have few words after entity replace
      if subject is not '':
        # Present time
        if re.search('former|actual|is|current',subject, re.IGNORECASE):
          info.append('Entity:'+entity.replace(' ','_')+' is '+subject+' of '+url)   # Create information
        # Previous time
        else:
          info.append('Entity:'+entity.replace(' ','_')+' was '+subject+' of '+url)  # Create information
  #return info

###############################################################
# Method for extract information about extracted entity
###############################################################
def startInformationExtraction():
  cnt = 0
  # Output file
  #if os.path.exists(PATHPREFIX+'FinalInformation/'+socket.gethostname()+'-extracted.info'):
  if True:
    with open(PathPrefix+'FinalInformation/'+socket.gethostname()+'-extracted.info-extracted','w+') as outputFile:
      outputFile.write('Input: '+socket.gethostname()+'-extracted.info\n')
      # Input file
      with open(PathPrefix+'FinalInformation/'+socket.gethostname()+'-extracted.info','r') as inputFile:
      #with open(PathPrefix+'results/Origins_of_the_American_Civil_War_overene_odkazy.checked','r') as inputFile:
        for line in inputFile:
          # Get data from input file
          data = re.search('([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\n]+)\n', line)
          if data:
            cnt += 1
            entity = data.group(1)
            url = data.group(2)
            interest = data.group(3)
            sentences = data.group(4)
            # Parse information
            extractedInformation = getInfo(sentences,entity,url,interest)
            if extractedInformation is not '':
              outputFile.write(extractedInformation+'\n')

###############################################################
# Main
###############################################################
if __name__ == "__main__":
  startInformationExtraction()
  sys.exit(0)