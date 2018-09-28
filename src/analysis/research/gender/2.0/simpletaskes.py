#一些简单的任务
from pymongo import MongoClient

#给用户原始特征添加性别数据，并写到一个新的collection中
def addGendertoOriFeature(dbname, collectionName, completeUserFeature):

    def getGender(uid):
        conn = MongoClient('192.168.1.198', 27017)
        db = conn['hupu']
        collection = db['hupuUserInfo']
        gender = collection.find_one({'uid': uid})
        if 'gender' in gender:
            return 1 if gender['gender']=='f' else 0
        else:
            return -1
    conn = MongoClient('192.168.1.198', 27017)
    db = conn[dbname]
    collection = db[collectionName]
    count = 0
    for data in collection.find({}):
        gender = getGender(data['uid'])
        if gender==-1:
            continue
        else:
            data['gender'] = gender
            db[completeUserFeature].insert(data, check_keys=False)
        #break
        count += 1
        print(gender, count)

if __name__ == '__main__':
    addGendertoOriFeature('hupu', 'oriUserFeature','completeUserFeature')