import sklearn as sk
import numpy as np
import pandas as pd
import random
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold as kf

class StackingClassifier():

    def __init__(self):
        self.baseModels = {}
        self.metaModel = None
        self.clfNames = []

    def setBaseModels(self, baseModels={}):  # 设置初级分类器
        """baseModels的元素是一个dict，比如{"clname": SVC()}"""
        self.baseModels = baseModels
        self.clfNames = list(baseModels.keys())

    def setMetaModel(self, metaModel=None):  # 设置次级分类器
        self.metaModel = metaModel

    def fit(self, XMap={}, Y=None):  # 训练分类器
        "XMap是一个dict,key为初级分类器的名字，value是对应的特征，要求是numpy.array"
        # 训练初级分类器
        for modelName in self.baseModels:
            self.baseModels[modelName].fit(XMap[modelName], Y)

        # 计算分类器的输出
        basePrediction = np.zeros((len(Y), 1))
        for modelName in self.clfNames:
            baseProbability = self.baseModels[modelName].predict_proba(XMap[modelName])
            basePrediction = np.concatenate((basePrediction, baseProbability), axis=1)
        basePrediction = basePrediction[:, 1:]
        # 训练次级分类器
        self.metaModel.fit(basePrediction, Y)

    def predict(self, XMap={}):
        featureNum = len(XMap[self.clfNames[0]])
        basePrediction = np.zeros((featureNum, 1))
        for modelName in self.baseModels:
            baseProbability = self.baseModels[modelName].predict_proba(XMap[modelName])
            basePrediction = np.concatenate((basePrediction, baseProbability), axis=1)
        basePrediction = basePrediction[:, 1:]
        result = self.metaModel.predict(basePrediction)
        return result

    def kFoldValidatoin(self, XMap, Y, k=10, classNum=2):
        randomIndex = random.sample(range(len(Y)), len(Y))
        for clfName in XMap:
            XMap[clfName] = XMap[clfName][randomIndex]
        y = Y[randomIndex]
        cmTotal = np.zeros((classNum, classNum))
        index = kf(n_splits=k).split(list(range(len(Y))))
        for line in index:
            trainIndex = line[0]
            testIndex = line[1]
            trainX, testX = {}, {}
            for clfName in XMap:
                trainX[clfName] = XMap[clfName][trainIndex]
                testX[clfName] = XMap[clfName][testIndex]
            trainy = y[trainIndex]
            testy = y[testIndex]
            self.fit(trainX, trainy)
            y_pred = self.predict(testX)
            cm = confusion_matrix(testy, y_pred)
            cmTotal += np.array(cm)
        print(cmTotal)


if __name__ == '__main__':
    clf = StackingClassifier()
    from sklearn import datasets
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.naive_bayes import GaussianNB, BaseNB

    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    clf.setBaseModels(baseModels={'desisionTree': DecisionTreeClassifier(),
                                  'mlp': MLPClassifier(hidden_layer_sizes=(50)),
                                  'KNN': KNeighborsClassifier(n_neighbors=10), "NB": GaussianNB()})