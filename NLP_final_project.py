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
    #print(keywordQuestion)
    #print(nameQuestion)

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
                
        #print(oq)
        
        #for j in range(0, len(tmp)): 
        oqlist.append(oq)
        targetList.append(tmp)
        targetAnswerList.append(ttmp)
        
        
        '''
            if (keyw == 1):
                break
            try:
                for k in range(0, len(keywordQuestion)): 
                    if keywordQuestion[k] in tmp[j]:
                        keyw = 1
                        targetList.append(tmp)
                        targetAnswerList.append(ttmp)
                        break
            except:
                text = '輸入錯誤！ 請重新輸入問題！'
                return text
                '''
    #print(len(oqlist))
    #print(len(targetList))
    n = len(targetList)
    i = 0
    for ii in range(0, n):
        if i > n:
            break
        optmp = ''
        tmp = ''
        #print(targetList)
        #print('')
        for j in range(0, len(targetList[i])):
            tmp = tmp + targetList[i][j]
        for j in range(0, len(oqlist[i])):  
            optmp = optmp + oqlist[i][j]
            '''
        if len(nameQuestion) > 0:
            for k in range(0, len(nameQuestion)):
                if nameQuestion[k] in targetList[i]:
                    targetQuestionList.append(tmp)
                    break
                else:
                    #print("del " + str(targetList[i]))
                    del targetList[i]
                    del targetAnswerList[i]
                    n = n - 1
                    i = i - 1
                    break
        else:
            '''
        targetQuestionList.append(optmp)
        i = i + 1
        

    #print(targetList)
    #print('')
    try:
        targetSnowNLP = SnowNLP(targetList)
    except:
        text = '本問題不在資料庫中！ 請重新輸入問題！'
        return text
    TargetSim = targetSnowNLP.sim(extractQuestion)
    
    
    #print(targetSnowNLP.tf)
    #print(targetQuestionList)
    #print(segQuestion)
    #print(extractQuestion)
    #print('')
    #print(targetList)
    #print('')
    
    #print(TargetSim)

    #rt = ''
    #for i in range(0, len(TargetSim)):
    #    if TargetSim[i] > 0:
    #        rt = rt + targetQuestionList[TargetSim.index(TargetSim[i])] + '\n\n'
            
    if (max(TargetSim) > 5):
        score = max(TargetSim)
        #if max(TargetSim) < 0:
        #    score = -max(TargetSim)
            #text = '本次搜尋分數: ' + str(score) + '\n' + '\n' + '搜尋對應問題： \n' + targetQuestionList[TargetSim.index(min(TargetSim))] + '\n' + '\n' + '搜尋對應回答： \n' + targetAnswerList[TargetSim.index(min(TargetSim))]
            #text = targetQuestionList[TargetSim.index(max(TargetSim))]
            #return text
        text = '本次搜尋分數: ' + str(score) + '\n' + '\n' + '搜尋對應問題： \n' + targetQuestionList[TargetSim.index(max(TargetSim))] + '\n' + '\n' + '搜尋對應回答： \n' + targetAnswerList[TargetSim.index(max(TargetSim))]
        #text = targetQuestionList[TargetSim.index(max(TargetSim))]
    else:
        text = '本次搜尋分數: ' + str(max(TargetSim)) + '\n' + '\n' + '搜尋不到相對應的結果！ 請重新輸入問題！'
    return HanziConv.toTraditional(text)
print(nlp('!問題'))

'''
correct = 0
error = 0
error_sentence = []
error_search = []
with codecs.open('New.json', 'r', 'utf-8') as file:
    file.text = file.read()
    fileDictionary = json.loads(file.text)

with codecs.open('OP.json', 'r', 'utf-8') as file:
    file.text = file.read()
    OPfileDictionary = json.loads(file.text)

pos = 0
zero = 0
neg = 0
scorelist = []
#len(fileDictionary)
for i in range(0, len(fileDictionary)):
    t = OPfileDictionary[i]['question']
    tmp = ''
    for j in range(0, len(t)):
        tmp = tmp + t[j]
    #print(tmp)
    #print(t1)
    scorelist.append(nlp(tmp))
    if (nlp(tmp) > 0):
        pos = pos + 1
    elif (nlp(tmp) == 0):
        zero = zero + 1
    elif (nlp(tmp) < 0):
        neg = neg + 1
        
print('pos = ' + str(pos))
print('zero = ' + str(zero))
print('neg = ' + str(neg))
print('')
print(min(scorelist))

'''

'''
#len(fileDictionary)
for i in range(0, len(fileDictionary)):
    t1 = fileDictionary[i]['question']
    t = OPfileDictionary[i]['question']
    tmp = ''
    for j in range(0, len(t)):
        tmp = tmp + t[j]
    #print(tmp)
    #print(t1)
    if (nlp(t1) == tmp):
        correct = correct + 1
    else:
        error = error + 1
        error_sentence.append(tmp)
        error_search.append(nlp(t1))

print('correct = ' + str(correct))
print('error = ' + str(error))
print('rate = ' + str(correct/(correct + error)))
print('')
for i in range(0, len(error_sentence)):
    print(str(i+1) + '.' + error_sentence[i])
print('\n\n')
for i in range(0, len(error_search)):
    print(str(i+1) + '.' + error_search[i])    
'''
