#用机器学习算法预测用户的性别
import numpy as np
import pandas as pd
import sklearn as sk
from matplotlib import  pyplot as plt
from pymongo import MongoClient
from hupu.analisys.config import enviroment
from sklearn.linear_model import LogisticRegressionCV,LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, BaseNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble  import VotingClassifier, RandomForestClassifier
from sklearn.metrics import confusion_matrix
from matplotlib import pyplot as plt
from sklearn.cross_validation import KFold as kf
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import random
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
#获取用户的统计数据

def getConnectionMongo():
    conn = MongoClient(enviroment.MONGO_IP, 27017)
    return conn

class genderDetection():

    def __init__(self):
        self.stasticsData = None
        self.conn = self.getConnectionMongo()
        self.featureWords = []#用于构建特征的词语
        self.featureNames = []
        self.featurePos = []
        self.featureChars = []
        self.stopWords = set({})
        self.N_word, self.N_pos, self.N_char = 5000, 20, 2000
        self.count = 200000
    def initStopWords(self, path):
        with open(path, 'r', encoding="utf8") as f:
            lines = f.readlines()
            lines = list(map(lambda x: x.replace("\n", ""), lines))
        self.stopWords = set(lines)

    def getConnectionMongo(self):
        conn = MongoClient(enviroment.MONGO_IP, 27017)
        return conn

    def getStasticsData(self):
        # '''
        conn = getConnectionMongo()
        db = conn.hupu  # 连接mydb数据库，没有则自动创建
        db_gender = db.hupuUserInfo
        # collection = db.userStastics  # 使用test_set集合，没有则自动创建
        collection = db.userFollStastics
        collection_long = db.userFollStastics_med

        data = collection.find({}, {"detail": 1}).batch_size(1000)
        count = 0
        self.stasticsData = []
        stasticsUID = []
        for line in data:
            uid = line['_id']
            t1 = time.time()
            genderData = list(db_gender.find({"_id": uid}, {"gender": 1, 'onlineTime':1,
                        'HPLevel':1, 'communityRPScore':1}))
            t2 = time.time()
            if len(genderData)==0 or "gender" not in genderData[0]:
                continue
            gender = genderData[0]["gender"]
            genderData = genderData[0]
            genderData['gender'] = 1 if gender=="m" else 0
            if random.uniform(0,1)>0.05 and gender=='m':
                continue

            detail = line['detail']
            thisData = line['detail']['follContentFeatrue']

            if len(thisData)>200:
                wcpMap = self.featureExtractionFromWords(thisData)
                wcpMapTemp = wcpMap
                wcpMap = {'uid': uid, **wcpMapTemp, **genderData,
                          'followPostNumber': line['detail']['followPostNumber'],
                          'lightedNumber': line['detail']['lightedNumber'],
                          'footBallIndex': line['detail']['footballIndex'],
                          'basketballIndex': line['detail']['basketballIndex']
                          }
                collection_long.insert({**line, **genderData})
                print(count, len(wcpMap), gender)
                count += 1
                self.stasticsData.append(wcpMap)
            if count > self.count:
                break
        data = pd.DataFrame(self.stasticsData)
        pickle.dump(data, open('data.pkl', 'wb'))
        # '''
        droppList = []
        # droppList = ['followPostNumber', 'lightedNumber', 'HPLevelInc','footBallIndex',
        #              'communityRPScoreInc','communityRPScore','basketballIndex',
        #              'onlineTime']
        data = pickle.load(open(r'data.pkl', 'rb')).drop(droppList, axis=1)
        data = data.fillna(data.median())
        # print(data.isnull())
        self.stasticsData = data.reset_index(drop=True)

        # print(self.stasticsData)

    def featureExtractionFromWords(self, aWordFreqMap):
        def initACleanMap(keyList, addDtr = ""):
            tempMap = {}
            for key in keyList:
                tempMap[addDtr + key] = 0
            return tempMap

        line = aWordFreqMap
        wordFreqMap = initACleanMap(self.featureWords, addDtr='word_')
        print("词频字典的大小是", len(wordFreqMap), len(self.featureWords))
        posTagFreqMap = initACleanMap(self.featurePos, addDtr='pos_')
        charFreqMap = initACleanMap(self.featureChars, addDtr='char_')
        # print(self.featureWords)
        # print(self.featureChars)

        for aWordFreq in line:
            try:
                word, posTag = aWordFreq['word'].split("/")
            except:
                continue
            freq = int(aWordFreq['freq'])
            #
            if "word_" + word in wordFreqMap:
                wordFreqMap["word_" + word] += freq

            # print(wordFreqMap)
            if "pos_" + posTag in posTagFreqMap:
                posTagFreqMap[ "pos_" + posTag] += freq

            for char in word:
                if "char_" + char in charFreqMap:
                    charFreqMap["char_" +char] += freq
        features = {**wordFreqMap, **charFreqMap, **posTagFreqMap}
        # print(features)
        return features

    def loadFeatureWords(self, path):
        import re
        N_word, N_pos, N_char = self.N_word, self.N_pos,self.N_char
        with open(path, 'r', encoding="utf8") as f:
            lines = f.readlines()
            lines = list(map(lambda x: x.replace("\n", ""), lines))
        words = lines[1].split(" ")[1:int(0.5*N_word)] + \
                lines[4].split(" ")[1:N_word-int(0.5*N_word)]
        print("特征词的数量是", len(words), N_word, len(lines[1].split(" ")), lines[1])
        words = list(map(lambda x: x.replace('\'', ''), words))
        posTags =lines[2].split(" ")[1:int(0.5*N_pos)] + \
                 lines[5].split(" ")[1:N_pos-int(0.5*N_pos)]
        posTags = list(map(lambda x: x.replace('\'', ''), posTags))
        chars = lines[0].split(" ")[1:int(0.5*N_char)] + \
                lines[3].split(" ")[1:N_char-int(0.5*N_char)]
        chars = list(map(lambda x: x.replace('\'', ''), chars))
        self.featureWords = list(sorted(set(words)))#用于构建特征的词语
        self.featurePos = list(sorted(set(posTags) - set(words)))
        self.featureChars = list(sorted(set(chars) - set(words) - set(posTags)))

    def updateWordFreq(self, resultWordFreqMap, aWordFreList):
        # 更新词频map里的词频。由于是浅拷贝，会修改引用对象的取值。这样做的好处是免去了新建一个对象的成本。
        for line in aWordFreList:
            try:
                word, pos = line['word'].split("/")
            except:
                continue
            # print(word, self.stopWords)
            import re
            if word in self.stopWords or len(re.findall("[0-9]", word)) > 0:
                # print("挺用词", word)
                continue
            num = int(line["freq"])
            if word in resultWordFreqMap:
                resultWordFreqMap[word] += num
            else:
                resultWordFreqMap[word] = num
        return resultWordFreqMap

    def getCharFreq(self, wordFreqList):
        def splitWordIntoChars(aUserWordFreqList):
            # 把词频map里的字符频率统计出来，形成一个新的map
            charFreqList = []
            for wordFreq in aUserWordFreqList:
                try:
                    word, pos = wordFreq['word'].split("/")
                except:
                    continue
                if word in self.stopWords:
                    continue
                freq = int(wordFreq['freq'])
                for char in word:
                    charFreqList.append({'word': char + "/" + pos, "freq": freq})
            return charFreqList

        res = {}
        for line in wordFreqList:
            charFreqList = splitWordIntoChars(line)  # 借用统计词频的函数，统计这个字符频率map里的字符频率
            self.updateWordFreq(res, charFreqList)
        freqSorted = sorted(res.items(), key=lambda x: x[1], reverse=True)
        return freqSorted

    def getPosFreq(self, wordFreqList):
        def splitWordIntoChars(aUserWordFreqList):
            # 把词频map里的字符频率统计出来，形成一个新的map
            posFreqList = []
            for wordFreq in aUserWordFreqList:
                try:
                    word, pos = wordFreq['word'].split("/")
                except:
                    continue
                if word in self.stopWords:
                    continue
                freq = int(wordFreq['freq'])
                posFreqList.append({'word': pos + "/" + pos, "freq": freq})
            return posFreqList

        res = {}
        for line in wordFreqList:
            posFreqList = splitWordIntoChars(line)  # 借用统计词频的函数，统计这个字符频率map里的字符频率
            self.updateWordFreq(res, posFreqList)
        freqSorted = sorted(res.items(), key=lambda x: x[1], reverse=True)
        return freqSorted

    def addGender(self):
        maleData = self.stasticsData.loc[self.stasticsData['gender'] == 1]
        femaleData = self.stasticsData.loc[self.stasticsData['gender'] == 0]
        maleData = maleData.sample(n=int(len(femaleData)*1))
        # print(self.stasticsData)
        self.stasticsData = femaleData.append(maleData)
        self.stasticsData = self.stasticsData.sample(frac=1)
        self.labels = self.stasticsData['gender'].values
        self.features = self.stasticsData.drop(["gender", 'uid'], axis=1).values

        self.labels = list(map(lambda x: [x], self.labels))
        self.labels = np.array(self.labels).reshape(len(self.labels), 1)

    def crossValidation(self):
        count = 1
        totalCM = np.zeros([2,2])
        # self.features = np.array(self.features)
        # self.labels = np.array(self.labels)
        # clf = DecisionTreeClassifier(max_depth=10)
        # clf = RandomForestClassifier(n_estimators=30, max_depth=6,random_state=666)
        # clf = AdaBoostClassifier(base_estimator=DecisionTreeClassifier(max_depth=10), n_estimators=20)
        clf = MLPClassifier(hidden_layer_sizes=(200,))
        # clf = LogisticRegression(max_iter=1000, solver='lbfgs', C=100)
        # clf = GradientBoostingClassifier(n_estimators=20)
        # clf = SVC(C=0.8)
        # clfList = [
        #     ["AD", AdaBoostClassifier(base_estimator=DecisionTreeClassifier(max_depth=10), n_estimators=20)],
        #     ["gbdt", GradientBoostingClassifier(n_estimators=20)],
        #     ["LR", LogisticRegression(max_iter=1000, solver='lbfgs', C=100)],
        #     ['desisionTree', DecisionTreeClassifier()],
        #            ['mlp', MLPClassifier(hidden_layer_sizes=(100, ))],
        #            ['KNN', KNeighborsClassifier(n_neighbors=20)]]
        # clf = VotingClassifier(clfList, voting='hard')
        # print(self.features)
        X_train, X_test = self.features, self.features

        from sklearn.preprocessing import RobustScaler
        norm_x = RobustScaler().fit(X_train)
        X_train, X_test = norm_x.transform(X_train), norm_x.transform(X_test)
        X_train, X_test = np.abs(X_train), np.abs(X_test)
        # print(X_train)
        y_train, y_test = self.labels, self.labels
        # featureProcessor = PCA(n_components=20)
        print(len(X_train),'asd', len(y_train))
        # print(X_train,'asd', y_train)
        def aaa(X, L):
            res = []
            for i in range(L):
                line = X[i]
                tres =  []
                for n in line:
                    tres.append(n)
                res.append(tres)
            return np.array(res)
        X_train, X_test = aaa(X_train, len(y_train)), aaa(X_test, len(y_test))
        X_train,X_test = X_train[:,:], X_test[:,:]
        y_train, y_test = np.array(y_train), np.array(y_test)
        featureNameIndex = range(len(X_train[0]))
        print("原始的特征数是", len(X_train[0]))
        # featureProcessor = PCA(n_components=10)

        # featureProcessor = LinearDiscriminantAnalysis(n_components=150).fit(X_train, y_train)
        featureProcessor = SelectKBest(chi2, k=1000)#.fit(features, labels)

        featureProcessor.fit(X_train, y_train)
        pickle.dump(featureProcessor, open('featureProcessor.pkl', 'wb'))
        featureProcessor = pickle.load(open('featureProcessor.pkl', 'rb'))
        X_train = featureProcessor.transform(X_train)
        X_test = featureProcessor.transform(X_test)


        featureNameIndex = featureProcessor.transform(np.array([featureNameIndex]))[0]
        featureNameList = np.array(self.featureNames)[featureNameIndex]
        print("提取出来的特征名称是", featureNameList)
        clf.fit(X_train, y_train)
        pred_train = clf.predict(X_train)
        y_train = list(y_train)
        cm = confusion_matrix(y_train, pred_train)
        print("第", count, "轮训练集里的表现\n", cm)
        pred = clf.predict(X_test)
        y_test = list(y_test)
        cm = confusion_matrix(y_test, pred, labels=[0, 1])
        totalCM = totalCM + np.array(cm)
        print("第", count, "轮测试集里的表现\n", cm)
        # print(X_test)
        print("####################################")
        count += 1
        print("混淆矩阵的和是\n", totalCM, "准确率是",
              (totalCM[0][0] + totalCM[1][1])/(sum(sum(totalCM))))

def classIt():
    t1 = time.time()
    genderAnnalysis = genderDetection()
    genderAnnalysis.initStopWords(r"C:\Users\Administrator\PycharmProjects\test\hupu\analisys\research\gender\HIT_stop_words.txt")
    genderAnnalysis.getStasticsData()


from matplotlib import pyplot as plt
def DE():
    genderAnnalysis = genderDetection()
    genderAnnalysis.initStopWords(
        r"C:\Users\Administrator\PycharmProjects\test\hupu\analisys\research\gender\HIT_stop_words.txt")
    genderAnnalysis.loadFeatureWords(r"C:\Users\Administrator\PycharmProjects\test\hupu\analisys\research\gender\genderFeature.txt")
    print("开始添加性别。", genderAnnalysis.featureChars)
    genderAnnalysis.getStasticsData()
    genderAnnalysis.addGender()
    genderAnnalysis.crossValidation()




import pickle
from sklearn.metrics import confusion_matrix
from sklearn import ensemble
import time
if __name__ == '__main__':
    DE()
    # classIt()



