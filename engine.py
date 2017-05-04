# encoding: UTF-8
from stemming import PorterStemmer
from doc import Dictionary
import math
import operator
import re


class Engine:
    ''' addressing query input by user, search similar document
        and return top 6 result
        @author: Shiqu Chen
    '''

    def __init__(self, docList, idf, N):
        '''@para docList: Document object list
            idf: Dictionary
        '''
        self.docList = docList
        self.idf = idf
        self.simiDict = []
        self.similarWord()
        self.N = N

    def similarWord(self):
        '''read tresaurus file'''
        stemmer = PorterStemmer()
        mark = re.compile('\w+')
        with open('similar.txt', encoding='utf-8') as f:
            for line in f.readlines():
                words = mark.findall(line)
                if len(words) != 0:
                    # stemming
                    w = []
                    for word in words:
                        w.append(stemmer.stem(word, 0, len(word) - 1))
                    self.simiDict.append(w)

    def querySplit(self, query):
        '''split query into seperate terms and stemming'''
        queryTerms = []
        query = query.lower()
        terms = query.split()
        # stemming
        stemmer = PorterStemmer()
        for word in terms:
            queryTerms.append(stemmer.stem(word, 0, len(word) - 1))

        return queryTerms

    def queryVector(self, queryTerms):
        '''term frequency
            @return queryV: Dictionary,query vector
        '''
        queryV = Dictionary()
        for word in queryTerms:
            queryV[word] = 1
        return queryV

    def weightQuery(self, model, queryV):
        '''calculate tf-idf for query vector
            @para model: different weighting model
            "tf": weight = tf
            "tf-idf": weight = tf * idf
        '''
        if model == 'tf':
            pass
        if model == "tf-idf":
            for key in queryV.keys():
                queryV[key] = queryV[key] * self.idf[key]

    def normalizeQuery(self, queryV):
        '''cosine normalization'''
        length = 0
        for key in queryV.keys():
            length += math.pow(queryV[key], 2)
        length = math.sqrt(length)

        # normalize
        for key in queryV.keys():
            queryV[key] = queryV[key] / length

    def weightDoc(self):
        # weight document vector
        for doc in self.docList:
            doc.weightDoc('tf-idf', self.idf)
            doc.normalizeDoc()

    def cosineScore(self, queryV):
        '''calculate score for each documents'''
        for doc in self.docList:
            s = 0
            docV = doc.getWeight()
            for key in queryV.keys():
                s += docV[key] * queryV[key]
            doc.setScore(s)

    def extraScore(self, queryV):
        '''add 0.5 to the document if query term appear in the title'''
        for doc in self.docList:
            title = doc.getTitle().lower()
            for word in queryV.keys():
                if word in title:
                    doc.setScore(doc.getScore() + 0.5)

    def ranking(self):
        '''sorting result
            @return format: [(index,score),(index,score),...]
        '''
        length = len(self.docList)
        # score dictionary
        docScore = Dictionary()
        for i in range(length):
            docScore[i] = self.docList[i].getScore()

        # sorting from small to large
        sortScore = sorted(docScore.items(), key=operator.itemgetter(1))
        return sortScore

    def expansion(self, queryTerm):
        '''extend the query base on the tresaurus'''
        newQuery = set()
        for term in queryTerm:
            for item in self.simiDict:
                if term in item:
                    for t in item:
                        newQuery.add(t)
                    break

        newQuery = list(newQuery)
        return newQuery

    def display(self, docScore, queryTerm):
        '''show result'''
        print("search result:\n")
        # reverse
        n = self.N
        docScore = docScore[::-1]
        if len(self.docList) < n:
            r = len(self.docList)
        else:
            r = n
        for i in range(r):
            doc = self.docList[docScore[i][0]]
            print("%s     %f" % (doc.getTitle(), doc.getScore()))
            print(doc.getUrl())
            print(doc.readfile(20))
            print('\n\n')

        # print("query expansion:")
        # self.expansion(queryTerm)

    def start(self):
        ''' start search engine
            enter "stop" to end
        '''
        self.weightDoc()
        print(self.simiDict)

        while 1:
            query = input("please typing your query(typing stop to end)> ")
            query = query.strip()
            # if query is stop, end routine
            if query == 'stop':
                break

            # query split and stemming
            terms = self.querySplit(query)

            # weight query
            queryV = self.queryVector(terms)
            self.weightQuery("tf", queryV)
            self.normalizeQuery(queryV)

            self.cosineScore(queryV)
            self.extraScore(queryV)

            docScore = self.ranking()

            print("*********************************************************")
            print("Query: %s" % query)
            self.display(docScore, terms)
            print("*********************************************************")
            # reverse
            docScore = docScore[::-1]
            if docScore[2][1] == 0:
                newTerms = self.expansion(terms)
                queryV = self.queryVector(newTerms)
                self.weightQuery("tf", queryV)
                self.normalizeQuery(queryV)

                self.cosineScore(queryV)
                self.extraScore(queryV)

                docScore = self.ranking()
                newQ = ''
                for t in newTerms:
                    newQ = newQ + ' ' + t
                print("**************************************************")
                print("Query Expension: %s" % newQ)
                self.display(docScore, terms)
                print("**************************************************")
                docScore = docScore[::-1]

        print('engine closed')
