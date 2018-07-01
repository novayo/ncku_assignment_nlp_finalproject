# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 20:00:34 2018

@author: adadz
"""

from collections import OrderedDict
from multiprocessing import Pool
import socket
import time
import json
import codecs
from hanziconv import HanziConv

with codecs.open('New.json', 'r', 'utf-8') as file:
    file.text = file.read()
    fileDictionary = json.loads(file.text)
    
json_data = []
for i in range(0, len(fileDictionary)):
    tmp = fileDictionary[i]['question']
    s = HanziConv.toSimplified(tmp)
    
    data = {}
    data['question'] = s
    data['answer'] = fileDictionary[i]['answer']
    json_data.append(json.dumps(data))
t = []
for i in range(0, len(fileDictionary)):
    t.append(json.loads(json_data[i]))
print(t)
#print(unicode(json_data, encoding='unicode_escape'))