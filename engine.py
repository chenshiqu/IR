# encoding: UTF-8
from stemming import PorterStemmer
from doc import Dictionary
import math


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
        stem = PorterStemmer()
        for word in terms:
            queryTerms.append(stem(word, 0, len(word) - 1))
        # initial query vectory
        for word in queryTerms:
            self.queryV[word] = 1
        return queryTerms

    def docVector(self, queryTerms):
        '''term frequency and normalization
            @return docV: list, document vector
        '''
        docV = []
        for doc in self.docList:
            temp = Dictionary()
            terms = doc.getTerm()
            for term in queryTerms:
                temp[term] = terms[term]
            docV.append(temp)
        return docV

    def queryVector(self, queryTerms):
        '''term frequency
            @return queryV: Dictionary,query vector
        '''
        queryV = Dictionary()
        for word in queryTerms:
            queryV[word] = 1
        return queryV

    def weightDoc(self, model, docV):
        '''calculate tf-idf for doc vector
            @para model: different weighting model
            "tf": weight = tf
            "tf-idf": weight = tf * idf
            "log": weight = (1 + log(tf)) * idf
            @return docV : list contains Dictionary
        '''
        if model == 'tf':
            return docV
        if model == 'tf-idf':
            for doc in docV:
                for key in doc.keys():
                    doc[key] = doc[key] * self.idf[key]
            return docV
        if model == 'log':
            for doc in docV:
                for key in doc.keys():
                    doc[key] = (1 + math.log(doc[key])) * self.idf[key]

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

    def normalizeDoc(self, docV):
        ''''cosine nomalization'''
        for doc in docV:
            # document length
            length = 0
            for key in doc.keys():
                length += math.pow(doc[key], 2)
            length = math.sqrt(length)

            # normalize
            for key in doc.keys():
                doc[key] = doc[key] / length

    def normalizeQuery(self, queryV):
        '''cosine normalization'''
        length = 0
        for key in queryV.keys():
            length += math.pow(queryV[key], 2)
        length = math.sqrt(length)

        # normalize
        for key in queryV.keys():
            queryV[key] = queryV[key] / length

    def start(self):
        ''' start search engine
            enter "stop" to end
        '''
        while 1:
            query = input("please typing your query(typing stop to end)> ")
            query = query.strip()
            # if query is stop, end routine
            if query == 'stop':
                break

            # query split and stemming
            terms = self.querySplit(query)
            # term frequency
            docV = self.docVector(terms)
            queryV = self.queryVector(terms)
            # weight
            w_docV = self.weightDoc('tf', docV)
            w_queryV = self.weightQuery('tf', queryV)

        print('engine closed')
