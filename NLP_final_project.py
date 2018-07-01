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
    Question = HanziConv.toSimplified(Question)
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
        return t1           
            
        
    if ('?' not in Question and '？' not in Question):
      return '請輸入問句！（記得加上問號）'
  
    #type in the question
    segQuestion = seg(Question) #段詞系統
    extractQuestion = []
    for i in range(0, len(segQuestion)):
        extractQuestion.append(segQuestion[i][0])
    
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
        keyw = 0
        
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
    
    #print(extractQuestion)
    #print('')
    #print(targetList)
    #print('')
    
    #print(TargetSim)

    if (max(TargetSim) != 0):
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
print(nlp('鲁夫是属于天然橡胶吗?或者是合成橡胶?'))

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
#print(nlp('自己第一次創作劇場版《ONE PIECE FILM STRONG WORLD》的感覺如何?')) #2.22e-16(max)
#print(nlp('一邊要創作劇場版要一邊進行極其嚴格的週刊連載，不是很不妙嗎?'))    #3.997(max)
#print(nlp('請問有什麼訣竅不會讓讀者感到膩味嗎?'))  #-3.8648594809738257(min)
#print(nlp('當初為什麼會畫海賊呢，是受了什麼作品的影響嗎?')) #22.333453995342428(max)
#print(nlp('請問偉大的航路會發生什麼事?會有船在天空中飛行嗎?')) #18.215966764501744(max)
#print(nlp('連載前情節都已經想好了嗎?')) #-3.8291114794674774(min)
#print(nlp('最後的結局已經決定了嗎?')) #-7.785188041541693(min)
#print(nlp('既然決定好了結局，到結局之前還可以有很長的時間來考慮呢?')) #-8.20839784078579(max)
#print(nlp('每個人物的情節都引起了讀者的共鳴，《ONE PIECE》是否覺得令人催淚呢?')) #33.696611101608006(max)
#print(nlp('描繪時自己有哭過嗎?')) #-8.788898309344875(max)
#print(nlp('有沒有絕對不描寫哪些事物的的規則嗎?')) #13.02640285135044(max)
#print(nlp('是在17歲獲得手塚獎後開始想要成為漫畫家的嗎?')) #15.9537503391368(max)
#print(nlp('獲得手塚獎時認為已經能行了嗎?')) #11.97208383944055(max)
#print(nlp('有過放棄當漫畫家的念頭嗎?')) #2.823443040935489(max)
#print(nlp('從事漫畫家這份工作高興嗎?')) #8.283158043246326(max)
#print(nlp(''))
#print(nlp(''))
#print(nlp(''))
#print(nlp(''))
#print(nlp(''))






