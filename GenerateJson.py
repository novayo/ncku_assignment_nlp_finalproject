# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 19:44:39 2018

@author: adadz
"""

from collections import OrderedDict
from multiprocessing import Pool
import socket
import time
import json
import codecs

#use Tr sentence extract
target_host = "140.116.245.151"
target_port = 2001

def seg(sentence):
    # create socket
    # AF_INET 代表使用標準 IPv4 位址或主機名稱
    # SOCK_STREAM 代表這會是一個 TCP client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client 建立連線
    client.connect((target_host, target_port))
    # 傳送資料給 target
    data = "seg@@" + sentence
    client.send(data.encode("utf-8"))
    
    # 回收結果信息
    data = bytes()
    while True:
        request = client.recv(8)
        if request:
            data += request
            begin = time.time()
        else:
            break

    WSResult = []
    response = data
    if(response is not None or response != ''):
        response = response.decode('utf-8').split()
        for resp in response:
            resp = resp.strip()
            resp = resp[0:len(resp)-1]
            temp = resp.split('(')
            word = temp[0]
            pos = temp[1]
            WSResult.append((word,pos))

    return WSResult

with codecs.open('New.json', 'r', 'utf-8') as file:
    file.text = file.read()

fileDictionary = json.loads(file.text)


targetList=[]
targetAnswerList=[]
for i in range(0, len(fileDictionary)):
    tmpList = []
    tmp = fileDictionary[i]['question']
    ttmp = fileDictionary[i]['answer']
    
    segtmp = seg(tmp)
    for j in range(0, len(segtmp)):
        tmpList.append(segtmp[j][0])
    targetList.append(tmpList)
    targetAnswerList.append(ttmp)
    

first = []
for k in range(0, len(targetList)):
    second = {}
    second['question'] = targetList[k]
    second['answer'] = targetAnswerList[k]
    first.append(second)
#print(first)

str1 = str(first)
print(str1)

'''
json website : https://jsoneditoronline.org/

open 新的json檔案，
複製print的結果到那個網站中，
就可以把print的內容加以整理了

'''

    

















