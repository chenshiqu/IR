# encoding: UTF-8
from stemming import PorterStemmer
from doc import Dictionary
import math
import operator


class Engine:
    ''' addressing query input by user, search similar document
        and return top 6 result
        @author: Shiqu Chen
    '''

    def __init__(self, docList, idf):
        '''@para docList: Document object list
            idf: Dictionary
        '''
        self.docList = docList
        self.idf = idf

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
            title = doc.getTitle()
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

    def display(self, docScore):
        '''show result'''
        # reverse
        docScore = docScore[::-1]
        for i in range(6):
            doc = self.docList[docScore[i][0]]
            print("%s     %f" % (doc.getTitle(), doc.getScore()))
            print(doc.getUrl())
            print(doc.readfile(20))
            print('\n\n')

    def start(self):
        ''' start search engine
            enter "stop" to end
        '''
        self.weightDoc()

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

            self.display(docScore)

        print('engine closed')
