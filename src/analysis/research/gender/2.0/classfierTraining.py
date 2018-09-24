import sys
import os
path = os.getcwd()
path = os.path.dirname(path)
sys.path.append(path)
path_src = path.split('src')[0]
sys.path.append(path_src + "src")#项目的根目录
import pymongo
import pandas as pd
import runTime
from analysis.config import enviroment
from src.analysis.algorithm.stacking import StackingClassifier

# userOriFeatureCollection = runTime.ORI_USER_FEATURE_SAMPLE_COLLECTION
# MONGO_IP, MONGO_PORT ,dbname, username, password = enviroment.MONGO_IP, enviroment.MONGO_PORT, \
#                                                           enviroment.MONGO_DB_NAME, None, None
# conn = MongoClient(MONGO_IP, MONGO_PORT)
# db = conn[dbname]
# db.authenticate(username, password)

def querySimpleFeatures(featureName='', goodFeatureNameList = []):
    collection = db[userOriFeatureCollection]
    data = collection.find({}, {'_id':1, "gender": 1, featureName: 1})#从mongo中查询这个特征以及对应的性别标签
    for line in data:
        line[featureName].update({'gender': line['gender']})
    dataList = list(lambda x: x[featureName], dataList)
    df = pd.DataFrame(data).fillnan(0)#每条记录的dict里没有的词语，pd会用nan来占据这个位置的value;没有出现的词语的频率就是0
    df = df[['gender'] + goodFeatureNameList]if goodFeatureNameList==[] else df#如果指定了优质特征，把这些特征提取出来
    db[featureName].drop()#删除原表
    db[featureName].insert(df.todict())
    
def queryGramFreqFeatures(featureName='', goodFeatureNameList = []):
    if len(goodFeatureNameList)==0:
        print("没有指定优质特征。")
        return None
    goodFeatureNameSet = set(goodFeatureNameList + ['gender'])#添加gender,以用于后面删除不好的特征
    collection = db[userOriFeatureCollection]
    data = collection.find({}, {'_id':1, "gender": 1, featureName: 1})#从mongo中查询这个特征以及对应的性别标签
    for line in data:
        line[featureName].update({'gender': line['gender']})
    dataList = list(lambda x: x[featureName], dataList)    
    for sample in dataList:
        for key in sample.keys():
            if key not in goodFeatureNameSet:
                del sample[key]#删除不是优质特征的条目
    df = pd.DataFrame(dataList).fillnan(0)
    db[featureName].drop()
    db[featureName].insert(df.todict())

def testClassifier(featureCollectionName = ""):
    def scala(x):
        res = []
        for i in range(len(x)):
            temp = []
            for n in x[i]:
                v = 1 if n>0 else 0
                temp.append(v)
            res.append(temp)
        return np.array(res)
    
    collection = db[featureCollectionName]
    data = collection.find({})#从mongo中查询这个特征以及对应的性别标签
    data = list(data)
    df = pd.DataFrame(data)
    clf = StackingClassifier()
    clf.setBaseModels({
        "DT": DecisionTreeClassifier(),#决策树
        'KNN': KNeighborsClassifier(n_neighbors=20),#最近邻
         "LR": LogisticRegression(max_iter=1000, solver='lbfgs', C=100)#逻辑回归
                                              })
    clf.setMetaModel(MLPClassifier(hidden_layer_sizes=(100,)))
    X, Y = df.drop(columns=['gender']).values, df['gender']
    X = scala(X)
    inputMap = {"DT": X, 'KNN': X, 'LR': X}
    clf.kFoldValidatoin(inputMap, Y, k=10)
    
if __name__ == '__main__':
    
    
    