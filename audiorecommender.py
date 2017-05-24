# Building an Audio Recommendation System with Spark
### Dataset: AudioScribbler dataset
### Author: Moorissa Tjokro

'''import libraries'''
import findspark
import pyspark
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.mllib import recommendation
from pyspark.mllib.recommendation import *

'''initialize spark in VM'''
findspark.init('/usr/local/bin/spark-1.3.1-bin-hadoop2.6/')
try:
    sc=SparkContext()
except:
    None

'''define variables'''
rawUserArtistData = sc.textFile("vagrant/user_artist_data.txt")
rawArtistData = sc.textFile("vagrant/artist_data.txt")
rawArtistAlias = sc.textFile("vagrant/artist_alias.txt")

'''define functions'''
def pairsplit(singlePair):
    splitPair = singlePair.rsplit('\t')
    if len(splitPair) != 2:
        return []
    else:
        try:
            return [(int(splitPair[0]), splitPair[1])]
        except:
            return []
artistByID = dict(rawArtistData.flatMap(lambda x: pairsplit(x)).collect())

def aliaslookup(alias):
    splitPair = alias.rsplit('\t')
    if len(splitPair) != 2:
        return []
    else:
        try:
            return [(int(splitPair[0]), int(splitPair[1]))]
        except:
            return []
artistAlias = rawArtistAlias.flatMap(lambda x: aliaslookup(x)).collectAsMap()
bArtistAlias = sc.broadcast(artistAlias)

def ratinglookup(x):
    userID, artistID, count = map(lambda line: int(line), x.split())
    finalArtistID = bArtistAlias.value.get(artistID)
    if finalArtistID is None:
        finalArtistID = artistID
    return Rating(userID, finalArtistID, count)

trainData = rawUserArtistData.map(lambda x: ratinglookup(x))
trainData.cache()

'''build model'''
model = ALS.trainImplicit(trainData, 10, 5)

'''test artist'''
spotcheckingID = 2093760
bArtistByID = sc.broadcast(artistByID)

rawArtistsForUser = (trainData
                  .filter(lambda x: x.user == spotcheckingID)
                  .map(lambda x: bArtistByID.value.get(x.product))
                  .collect())
print(rawArtistsForUser)

'''output recommendations'''
recommendations = map(lambda x: artistByID.get(x.product), model.call("recommendProducts", spotcheckingID, 10))
print(recommendations)
