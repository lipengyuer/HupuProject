#一些简单的任务
from pymongo import MongoClient
import numpy as np
import copy

#给用户原始特征添加性别数据，并写到一个新的collection中
def addGendertoOriFeature(dbname, collectionName, completeUserFeature):

    def getGender(uid, db):
        collection = db['hupuUserInfo']
        gender = collection.find_one({'uid': uid},{'gender':1})
        if gender!=None and 'gender' in gender:
            return 1 if gender['gender']=='f' else 0
        else:
            return -1

    conn = MongoClient('192.168.1.198', 27017)
    db = conn[dbname]
    collection = db[collectionName]
    count = 0
    for data in collection.find({}, {"uid":1, "wordFreq":1, "_id": 0}).batch_size(100):
        gender = getGender(data['uid'], db)
        if gender==-1:
            continue
        else:
            data['gender'] = gender
            db[completeUserFeature].insert(data, check_keys=False)
        #break
        count += 1
        print(gender, count)

import random
def downSampling4Man(completeUserFeature, completeUserFeatureSample):
    conn = MongoClient('192.168.1.198', 27017)
    db = conn['hupu']
    collection = db[completeUserFeature]
    db[completeUserFeatureSample].drop()
    uidSet = set({})
    for data in collection.find({}).batch_size(500):
        if (data['gender']==0 and random.uniform(0,1)>0.90) or data['gender']==1:
            pass
        else:
            continue
        if data['uid'] not in uidSet:
            uidSet.add(data['uid'])
            db[completeUserFeatureSample].insert(data, check_keys=False)

if __name__ == '__main__':
    #addGendertoOriFeature('hupu', 'oriUserFeatureAll_foll','completeUserFeature')
    downSampling4Man('completeUserFeature', 'completeUserFeatureSample')

