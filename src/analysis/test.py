import re
import runTime
def  initBloomFilter():
    for line in runTime.mongoCollection.find({}, {'_id':1}):
        print("布隆过滤器", line)
        runTime.BLOOMFILTER.add(line)
initBloomFilter()