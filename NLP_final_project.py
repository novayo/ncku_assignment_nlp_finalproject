from collections import OrderedDict
from multiprocessing import Pool
import socket
import time

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





import json
import codecs
import random
from snownlp import SnowNLP
from hanziconv import HanziConv
def nlp(Question):
    text = ""
    #file extract from CTBC.json
    with codecs.open('OP (Simple).json', 'r', 'utf-8') as file:
        file = file.read()
    fileDictionary = json.loads(file)
    
    with codecs.open('OP (Traditional).json', 'r', 'utf-8') as file2:
        file1 = file2.read()
    oqfileDictionary = json.loads(file1)

    if ('!問題' in Question or '！問題' in Question):
        t1 = ''
        for i in range(0, 5):
          j = random.randint(0, len(oqfileDictionary))
          tmp = oqfileDictionary[j]['question']
          ttmp = ''
          for k in range(0, len(tmp)):
            ttmp = ttmp + tmp[k]
          t1 = t1 + str(i+1) + '. ' + ttmp + '\n'
        return t1         
            
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

    f = open('pause.txt', 'r')
    stopword = f.read()
    stopwordlist = stopword.split('\n')
    for i in range(0, len(fileDictionary)):
        tmp = fileDictionary[i]['question']
        oq = oqfileDictionary[i]['question']
        ttmp = fileDictionary[i]['answer']
        
        for j in range(0, len(stopwordlist)):
            n = len(tmp)
            k = 0
            for kk in range(0, n):
              if (k > n):
                break
              if (stopwordlist[j] in tmp):
                tmp.remove(stopwordlist[j])
                k = k - 1
                n = n - 1
              k = k + 1
            if (stopwordlist[j] in extractQuestion):
              extractQuestion.remove(stopwordlist[j])
        
        oqlist.append(oq)
        targetList.append(tmp)
        targetAnswerList.append(ttmp)


    for i in range(0, len(targetList)):
        optmp = ''
        for j in range(0, len(oqlist[i])):  
            optmp = optmp + oqlist[i][j]
        targetQuestionList.append(optmp)

    
    targetSnowNLP = SnowNLP(targetList)
    TargetSim = targetSnowNLP.sim(extractQuestion)
    
    if (max(TargetSim) > 5):
        score = max(TargetSim)
        text = '本次搜尋分數: ' + str(score) + '\n' + '\n' + '搜尋對應問題： \n' + targetQuestionList[TargetSim.index(max(TargetSim))] + '\n' + '\n' + '搜尋對應回答： \n' + targetAnswerList[TargetSim.index(max(TargetSim))]
    else:
        text = '本次搜尋分數: ' + str(max(TargetSim)) + '\n' + '\n' + '本問題不在資料庫中！ 請重新輸入問題！'
    return text

