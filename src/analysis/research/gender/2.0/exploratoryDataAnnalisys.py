import sys
import os
path = os.getcwd()
path = os.path.dirname(path)
sys.path.append(path)
path_src = path.split('src')[0]
sys.path.append(path_src + "src")#项目的根目录
import pymongo
from  pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

userStasticsCollection = "userFeatureSample"
MONGO_IP, MONGO_PORT ,dbname, username, password = environment.MONGO_IP, environment.MONGO_PORT, \
                                                          environment.MONGO_DB_NAME, None, None
conn = MongoClient(MONGO_IP, MONGO_PORT)
db = conn[dbname]
db.authenticate(username, password)
collection = db[userStasticsCollection]

def compareSimpleFeatures(featureName=""):
    data = collection.find({}, {'_id':1, "gender": 1, featureName: 1})#从mongo中查询这个特征以及对应的性别标签
    dataList = list(map(lambda x: {'gender': x['gender'], **x[featureName]}, data))#把特征和性别标签放在一个一层的map中
    df = pd.DataFrame(data)
    dataF, dataM = df[df['gender']==1], df[df['gender']==0]#把男性和女性的数据分组
    #删掉两份数据中的性别字段
    dataF = dataF.drop(columns=['gender'])
    dataM = dataM.drop(columns=['gender'])
    #求两份数据里，各个特征的平均值
    meanF, meanM = dataF.mean(),dataM.mean()
    colNames = list(meanF.columns)#字段名列表，用于画x轴刻度
    ax = plt.subplot(1,1,1)
    p1, = ax.plot(meanF)
    p2, = ax.plot(meanM)
    plt.xticks(colNames)
    plt.xlabel(featureName)
    plt.ylabel("mean frequency")
    plt.legend(handles = [p1, p2], labels = ["female", 'male'])
    plt.show()

def compareLengthFeatures():
    compareSimpleFeatures("sentenceLengthFeatures")

def specialCharFeatures():
    compareSimpleFeatures("specialCharFreq")

def functionWordFeatures():
    compareSimpleFeatures("functoinWordFreq")

def punctuationMarkFeatures():
    compareSimpleFeatures("punctuationMarkFreq")

#################################################
#分析词频，ngram频率,postagNgram频率。这几种特征的特点是，维度很高，需要首先用一定的方法，
#选取较好的特征，然后分析。这样做的目的是发现一些男女差异较大的地方，然后展示出来。
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest

#获取词汇表,并统计所有词语的频数,文档频率
def getWordFreqDocumentFreq(userWordFreqMapList, jobName = 'wordFreqDocumentFreq'):
    wordFreqMap, ducumentFreqMap = {}, {}
    for userWordFreqMap in userWordFreqMapList:
        for word in userWordFreqMap:
            if word in wordFreqMap:
                wordFreqMap[word] += userWordFreqMap[word]#把该用户的这个词语的频数累加上
                ducumentFreqMap[word] += 1#这个用户使用了这个词语，文档频率加一
            else:
                wordFreqMap[word] = 1
                ducumentFreqMap[word] = 1
    print(jobName, "原始词汇表的大小是", len(userWordFreqMap))
    N = 50
    wordFreqTopN = sorted(wordFreqMap.items(), key= lambda x: x[1])
    documentFreqTopN = sorted(ducumentFreqMap.items(), key= lambda x: x[1])
    print("词频top N 是：")
    for line in wordFreqTopN[:N]:
        print(line[0], line[1])
        print("词频top N 是：")
    print("###################")
    print("文档频率top N 是:")
    for line in documentFreqTopN[:N]:
        print(line[0], line[1])
    print("###################")
    
    #把统计结果存储到文本文件，便于仔细分析
    with open(jobName + ".txt", 'w') as f:
        f.write("word wordFreq documentFreq\n")
        for i in range(len(documentFreqTopN)):
            f.write(wordFreqTopN[i][0] + " " + 
                    str(wordFreqTopN[i][1]) + " " + str(documentFreqTopN[i][1]) + '\n')
    #返回频率和文档频率都比较高的gram，作为较优特征
    res = set(map(lambda x: x[0], wordFreqTopN[:10000] + documentFreqTopN[:10000]))
    return res
            
def ngramFreatures(featureName=""):
    data = collection.find({}, {'_id':1, "gender": 1, featureName: 1})#从mongo中查询这个特征以及对应的性别标签
    
    #首先对所有的gram进行一个简单筛选，把普及率低于一定阈值(几乎所有人都不用的),总的使用次数小于一定阈值(大家都用过，然而昙花一现的)
    betterFeatureSet = getWordFreqDocumentFreq(data[featureName], jobName=featureName)
    betterFeatureSet.add("gender")
    #从通过初筛的所有gram中挑选使用率最高的10000个，进入下一步
    dataList = list(map(lambda x: x[featureName].update({"gender": x['gender']}), data))#把特征和性别标签放在一个一层的map中
    for sample in dataList:
        for key in sample.keys():
            if key not in betterFeatureSet:
                del sample[key]#删除不是优质特征的条目
    df = pd.DataFrame(dataList)
    features = df.drop(columns=['gender'])
    #选取最好的k个特征
    featureProcessor = SelectKBest(chi2, k=20)#.fit(features, labels)
    featureProcessor.fit(features, df['gender'])
    features = featureProcessor.transform(features)
    featureNames = list(features.columns)
    featureNameIndex = featureProcessor.transform(featureNames)
    print("被选中的特征是", featureNameIndex)#与图中的特征名核对一下
    dataF, dataM = df[df['gender']==1], df[df['gender']==0]#把男性和女性的数据分组
    #删掉两份数据中的性别字段
    dataF = dataF.drop(columns=['gender'])
    dataM = dataM.drop(columns=['gender'])
    #求两份数据里，各个特征的平均值
    meanF, meanM = dataF.mean(),dataM.mean()
    colNames = list(meanF.columns)#字段名列表，用于画x轴刻度
    ax = plt.subplot(1,1,1)
    p1, = ax.plot(meanF)
    p2, = ax.plot(meanM)
    plt.xticks(colNames)
    plt.xlabel(featureName)
    plt.ylabel("mean frequency")
    plt.legend(handles = [p1, p2], labels = ["female", 'male'])
    plt.show()
    
if __name__ == '__main__':
    #从抽样表中查询数据，然后查询出这些用户的数据存储到一个新的表中，用来分析
    #查看两种性别的语句长度特征，形成两条取值曲线来对比
    compareLengthFeatures()
    #特殊符号频率
    specialCharFeatures()
    #虚词频率
    functionWordFeatures()
    #标点符号频率
    punctuationMarkFeatures()
    #基于卡方检验选择用于判断性别的较好特征(词频，ngram等)，画图对比这些较好特征再两性中的分布差异。
    ngramFreatures(featureName='wordFreq')
    ngramFreatures(featureName='unigramFreq')
    ngramFreatures(featureName='bigram')
    ngramFreatures(featureName='postagBigramFreq')
    ngramFreatures(featureName='postagUnigramFreq')
    ngramFreatures(featureName='postagTrigramFreq')
    
    
