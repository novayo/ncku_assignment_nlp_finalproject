from collections import OrderedDict
from multiprocessing import Pool
import socket
import time
import json
import codecs
import random
from snownlp import SnowNLP
from hanziconv import HanziConv

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

def nlp(Question):
    #Question = HanziConv.toSimplified(Question)
    text = ""
  #file extract from CTBC.json
    with codecs.open('OP.json', 'r', 'utf-8') as file:
        file = file.read()
    fileDictionary = json.loads(file)
    
    with codecs.open('OP.json', 'r', 'utf-8') as file2:
        file1 = file2.read()
    oqfileDictionary = json.loads(file1)

    if ('!問題' in Question or '！問題' in Question):
        t1 = ''
        for i in range(0, 5):
          j = random.randint(0, len(fileDictionary))
          tmp = fileDictionary[j]['question']
          ttmp = ''
          for k in range(0, len(tmp)):
            ttmp = ttmp + tmp[k]
          t1 = t1 + str(i+1) + '. ' + ttmp + '\n'
        return  HanziConv.toTraditional(t1)          
            
    if ('?' not in Question and '？' not in Question):
      return '請輸入問句！（記得加上問號）'
  
    #type in the question
    segQuestion = seg(Question) #段詞系統
    extractQuestion = []
    for i in range(0, len(segQuestion)):
        extractQuestion.append(HanziConv.toSimplified(segQuestion[i][0]))
    
    #get targetList
    oqlist = []
    targetList=[]
    targetQuestionList=[]
    targetAnswerList=[]
    keywordQuestion = []
    nameQuestion = []
    
    for i in range(0, len(segQuestion)):
        if ('VC' in segQuestion[i] or 'VCL' in segQuestion[i] or 'Vk' in segQuestion[i] or 'Na' in segQuestion[i] or 'VG' in segQuestion[i] or 'Nb' in segQuestion[i] or 'Nv' in segQuestion[i] or 'Na' in segQuestion[i]  or 'PARENTHESISCATEGORY' in segQuestion[i]):  
            keywordQuestion.append(segQuestion[i][0])
        if('Nb' in segQuestion[i]):
            nameQuestion.append(segQuestion[i][0])

    #find key sentence in data
    for i in range(0, len(fileDictionary)):
        tmp = fileDictionary[i]['question']
        oq = oqfileDictionary[i]['question']
        ttmp = fileDictionary[i]['answer']
        
        for jj in range(0, len(tmp)):
            if ('?' in tmp):
                tmp.remove('?')
            elif ('，' in tmp):
                tmp.remove('，')
            elif ('「' in tmp):
                tmp.remove('「')    
            elif ('」' in tmp):
                tmp.remove('」')
            elif ('《' in tmp):
                tmp.remove('《')
            elif ('》' in tmp):
                tmp.remove('》')
            elif ('》' in tmp):
                tmp.remove('》')
            elif ('的' in tmp):
                tmp.remove('的')
            elif ('‧' in tmp):
                tmp.remove('‧')
            elif ('那' in tmp):
                tmp.remove('那')
            elif ('個' in tmp):
                tmp.remove('個')
            elif ('吗' in tmp):
                tmp.remove('吗')
            elif ('呢' in tmp):
                tmp.remove('呢')
        
        #for j in range(0, len(tmp)): 
        oqlist.append(oq)
        targetList.append(tmp)
        targetAnswerList.append(ttmp)
        
    n = len(targetList)
    i = 0
    for ii in range(0, n):
        if i > n:
            break
        optmp = ''
        tmp = ''
        for j in range(0, len(targetList[i])):
            tmp = tmp + targetList[i][j]
        for j in range(0, len(oqlist[i])):  
            optmp = optmp + oqlist[i][j]
        targetQuestionList.append(optmp)
        i = i + 1

    try:
        targetSnowNLP = SnowNLP(targetList)
    except:
        text = '本問題不在資料庫中！ 請重新輸入問題！'
        return text
    TargetSim = targetSnowNLP.sim(extractQuestion)
    
    if (max(TargetSim) > 5):
        score = max(TargetSim)
        text = '本次搜尋分數: ' + str(score) + '\n' + '\n' + '搜尋對應問題： \n' + targetQuestionList[TargetSim.index(max(TargetSim))] + '\n' + '\n' + '搜尋對應回答： \n' + targetAnswerList[TargetSim.index(max(TargetSim))]
    else:
        text = '本次搜尋分數: ' + str(max(TargetSim)) + '\n' + '\n' + '搜尋不到相對應的結果！ 請重新輸入問題！'
    return HanziConv.toTraditional(text)
