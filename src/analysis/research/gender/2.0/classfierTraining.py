import sys
import os
path = os.getcwd()
path = os.path.dirname(path)
sys.path.append(path)
path_src = path.split('src')[0]
sys.path.append(path_src + "src")#项目的根目录
import pymongo
import runTime
from analysis.config import enviroment
# userOriFeatureCollection = runTime.ORI_USER_FEATURE_SAMPLE_COLLECTION
# MONGO_IP, MONGO_PORT ,dbname, username, password = enviroment.MONGO_IP, enviroment.MONGO_PORT, \
#                                                           enviroment.MONGO_DB_NAME, None, None
# conn = MongoClient(MONGO_IP, MONGO_PORT)
# db = conn[dbname]
# db.authenticate(username, password)

def querySimpleFeatures(featureName='', goodFeatureNameList = []):
    collection = db[userOriFeatureCollection]
    data = collection.find({}, {'_id':1, "gender": 1, featureName: 1})#从mongo中查询这个特征以及对应的性别标签
    dataList = list(map(lambda x: x[featureName].update({"gender": x['gender']}), data))#把特征和性别标签放在一个一层的map中
    df = pd.DataFrame(data).fillnan(0)#每条记录的dict里没有的词语，pd会用nan来占据这个位置的value;没有出现的词语的频率就是0
    df = df[['gender'] + goodFeatureNameList]if goodFeatureNameList==[] else df#如果指定了优质特征，把这些特征提取出来
    db[featureName].insert(df.todict())
    
def queryGramFreqFeatures(featureName='', goodFeatureNameList = []):
    if len(goodFeatureNameList)==0:
        print("没有指定优质特征。")
        return None
    goodFeatureNameSet = set(goodFeatureNameList + ['gender'])#添加gender,以用于后面删除不好的特征
    collection = db[userOriFeatureCollection]
    data = collection.find({}, {'_id':1, "gender": 1, featureName: 1})#从mongo中查询这个特征以及对应的性别标签
    dataList = list(map(lambda x: x[featureName].update({"gender": x['gender']}), data))#把特征和性别标签放在一个一层的map中
    for sample in dataList:
        for key in sample.keys():
            if key not in goodFeatureNameSet:
                del sample[key]#删除不是优质特征的条目
    df = pd.DataFrame(dataList).fillnan(0)
    db[featureName].insert(df.todict())

if __name__ == '__main__':
    import sys
    import os
    path = os.getcwd()
    path = os.path.dirname(path)
    print(path)
    
    