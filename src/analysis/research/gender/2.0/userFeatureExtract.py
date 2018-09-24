import sys
import os
path = os.getcwd()
path = os.path.dirname(path)
sys.path.append(path)
path_src = path.split('src')[0]
sys.path.append(path_src + "src")#项目的根目录
from pyhanlp import HanLP
from pyhanlp import *
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
import time
from pymongo import MongoClient
from analysis.algorithm import splitSentence, nlp
from pyspark import SparkContext, SparkConf
import runTime
#词频
def wordFreq(wordsLists):
    wordFreqMap = {}
    for post in wordsLists:#遍历post
        for sentence in post:#遍历post的句子
            for word in sentence:#遍历句子的词语
                if word in wordFreqMap:
                    wordFreqMap[word] += 1
                else:
                    wordFreqMap[word] = 1
    return wordFreqMap

#字符ngram
def ngramFreq(postList, n=1):
    ngramFreqMap = {}
    for post in postList:
        for i in range(len(post)-n):
            ngram = post[i:i+n]
            if ngram in ngramFreqMap:
                ngramFreqMap[ngram] += 1
            else:
                ngramFreqMap[ngram] = 1
    return ngramFreqMap

#词性标签ngram
def postagNgramFreq(postagsLists, n=1):
    ngramFreqMap = {}
    for post in postagsLists:#遍历post
        for sentence in post:#遍历post的句子
            for i in range(len(sentence)-n):
                ngram = '_'.join(sentence[i:i+n])
                if ngram in ngramFreqMap:
                    ngramFreqMap[ngram] += 1
                else:
                    ngramFreqMap[ngram] = 1
    return ngramFreqMap

#特殊符号频率
def specialCharFreq(postList):
    specialMarks = "@#$%"
    specialMarkSet = set(list(specialMarks))
    markFreqMap = {}
    for post in postList:
        for i in range(len(post)):
            ngram = post[i]
            if ngram not in specialMarkSet:
                continue
            if ngram in markFreqMap:
                markFreqMap[ngram] += 1
            else:
                markFreqMap[ngram] = 1
    return markFreqMap

def nerFreq():
    #命名实体频率暂时不考虑
    pass

#统计虚词的词频
def functionWordFreq(wordsLists):
    functionWords = '自 自从 从 到 向 趁 按 按照 依照 根据 靠 拿 比 因 因为 为 由于 被 给 让 叫 归 由 对 对于 关于 跟 和 同 向 和 同 跟 与 及 或 而 而且 并 并且 或者 不但 不仅 虽然 但是 然而 如果 与其 因为 所以 的 地 得 之 者 着 了 过 看  的 来着 来 把 左右 上下 多 似的 一样 一般 所 给 连 的 了 吧 呢 啊 嘛 呗 罢了 也好 啦 喽 着呢 吗 呢 吧 啊 '
    functionWordSet= set(functionWords.split(' '))
    wordFreqMap = {}
    for post in wordsLists:#遍历post
        for sentence in post:#遍历post的句子
            for word in sentence:#遍历句子的词语
                if word not in functionWordSet:
                    continue
                if word in wordFreqMap:
                    wordFreqMap[word] += 1
                else:
                    wordFreqMap[word] = 1
    return wordFreqMap

#标点符号频率
def punctuationMarkFreq(postList):
    punctuationMarks = """：。«¨〃—～‖‘’“”。，、；：？！―〃～＂＇｀｜﹕﹗/\\"""
    marksSet = set(list(punctuationMarks))
    pmFreqMap = {}
    for post in postList:
        for i in range(len(post)):
            ngram = post[i]
            if ngram not in marksSet:
                continue
            if ngram in pmFreqMap:
                pmFreqMap[ngram] += 1
            else:
                pmFreqMap[ngram] = 1
    return pmFreqMap

    
#基于post列表，以及对应的每一句的分词结果和词性标注结果，来统计相关语言风格特征
def lengthFeature(sentencesList, wordsList, postagsList):
    res = {}
    charNumInSentence, count1 = 0, 0#统计句子的字符个数均值
    sentenceNumInPost, count2 = 0, 0#统计每个评论的句子个数均值
    for sentences in sentencesList:
        sentenceNumInPost += len(sentences)
        count2 += 1
        for sentence in sentences:
            count1 += 1
            charNumInSentence += len(sentence)
    charNumInSentence = charNumInSentence/count1 if count1>0 else 0
    sentenceNumInPost = sentenceNumInPost/count2 if count2>0 else 0
    res['charNumInSentence'] = charNumInSentence
    res['sentenceNumInPost'] = sentenceNumInPost
    wordNumTotal, count1 = 0, 0
    wordLength, count2 = 0, 0#统计每个词语的字符个数均值
    for wordList in wordsList:
        for words in wordList:
            count1 += 1
            wordNumTotal += len(words)
            for word in words:
                count2 += 1
                wordLength += len(word)
    # 统计句子的词语个数均值
    wordNumInSentence = wordNumTotal/count1 if count1>0 else 0
    wordLength = wordLength/count2 if count2>0 else 0
    # 统计每个评论的词语个数均值
    postNum = len(wordsList)
    wordNumInPost = wordNumTotal/postNum if postNum>0 else 0
    res['wordNumInSentence'] = wordNumInSentence
    res['wordLength'] = wordLength
    res['wordNumInPost'] = wordNumInPost
    #统计每个句子的标点个数均值
    postagNumTotal, count1 = 0, 0
    for postagList in postagsList:
        for postags in postagList:
            count1 += 1
            for postag in postags:
                if 'w' in postag:
                    postagNumTotal += 1
    postagNumInSentence = postagNumTotal/count1 if count1>0 else 0
    res['postagNumInSentence'] = postagNumInSentence
    return res

def getGender(uid, userInfoCollectionName):
    MONGO_IP, MONGO_PORT ,dbname, username, password = environment.MONGO_IP, environment.MONGO_PORT, \
                                                          environment.MONGO_DB_NAME, None, None    
    conn = MongoClient(MONGO_IP, MONGO_PORT)
    db = conn[dbname]
    db.authenticate(username, password)
    gender = db[userInfoCollectionName].find({"_id": uid}, {"gender": 1})
    if len(gender)==0:
        return None
    gender = gender[0]['gender']
    gender = 1 if gender=='f' else 0
    return gender

def extractTextFeatures(data, userInfoCollectionName=''):
    uid, postList = data[0], data[1]
    gender = 1
    gender = getGender(uid, userInfoCollectionName)
    if gender==None:#如果没有性别数据，这条数据无效
        return {}
    #获取分句，分词和词性标注结果
    sentencesLists, wordsLists, postagsLists = nlp.sentenceWordPostag(postList)
    #各类特征放在不同的key下
    featureMap = {'gender': gender,
                  "wordFreq": wordFreq(wordsLists), 
                  "unigramFreq": ngramFreq(postList, n=1),
                   'bigram': ngramFreq(postList, n=2), 
                  'postagUnigramFreq': postagNgramFreq(postagsLists, n=1), 
                  'postagBigramFreq': postagNgramFreq(postagsLists, n=2),
                   'postagTrigramFreq': postagNgramFreq(postagsLists, n=3), 
                   'specialCharFreq': specialCharFreq(postList),
                  'functoinWordFreq': functionWordFreq(wordsLists), 
                  'punctuationMarkFreq': punctuationMarkFreq(postList),
                  'sentenceLengthFeatures': lengthFeature(sentencesLists, wordsLists, postagsLists)}
    return featureMap


#向mongo插入一条数据
def saveRecord2Mongo(data, collectionName):
    MONGO_IP, MONGO_PORT ,dbname, username, password = environment.MONGO_IP, environment.MONGO_PORT, \
                                                          environment.MONGO_DB_NAME, None, None    
    conn = MongoClient(MONGO_IP, MONGO_PORT)
    db = conn[dbname]
    db.authenticate(username, password)
    collection = db[collectionName]
    collection.insert(data)
    
if __name__ == '__main__':
    conf = SparkConf().setAppName("hupu_user_feature_extraction")#配置spark任务的基本参数
    sc = SparkContext(conf = conf)#创建sc对象
    sc.addPyFile('/opt/dev/HupuPlay-master/hupu/analisys/research/gender/2.0/nlp.py')#添加自定义模块的本地或者hdfs路径，以后就可以使用这个模块里的函数了
    sc.addPyFile('/opt/dev/HupuPlay-master/hupu/analisys/research/gender/2.0/splitSentence.py')
    path_postData = "/user/mydata/hupu_bxj_advocate_post_dir/hupu_bxj_advocate_posts_4_new.txt"#post数据文件路径
    dataRDD = sc.textFile(path_postData)
    
    #去除换行符后，用分隔符分割开,然后以uid为key, post为value构建键值对rdd.部分uid是昵称，需要以str的形式存在
    noUID, noPost = 9, 8
    uidDataRDD = dataRDD.map(lambda x: x.replace('\n', '').split('#')).map(lambda x: (x[noUID], x[noPost]))
    #按照uid分组后，删除post个数小于阈值
    minPostNum = 50
    uidPostListRDD = uidDataRDD.groupByKey().mapValues(lambda x: list(x)[:200]).filter(lambda x: len(x[1])> minPostNum)
    #提取特征
    uidFeaturesRDD = uidPostListRDD.map(lambda x: extractTextFeatures(x, userInfoCollectionName=runTime.USER_INFO_COLLECTION)).\
                                              filter(lambda x: len(x[1])>0)#删掉特征个数为0,即没有性别数据的用户
    #保存结果到mongo
    uidFeaturesRDD.map(lambda x: saveRecord2Mongo({'_id': x[0], **x[1]}, runTime.ORI_USER_FEATURE_COLLECTION))#全部数据
    uidFeaturesRDD.sample(False, 0.01, 666).map(lambda x: saveRecord2Mongo({'_id': x[0], **x[1]},
                                                 runTime.ORI_USER_FEATURE_SAMPLE_COLLECTION))#抽样数据
    
    
    
    
    
    
    
