# encoding: UTF-8
import stemming
import re
import math


class Dictionary(dict):
    '''re define __missing__ function'''

    def __missing__(self, key):
        return 0


class Document:
    ''' a describe of a web page
        @author: Shiqu Chen
    '''

    def __init__(self, url, docID, fileName, fileType):

        self.url = url
        self.docID = docID
        self.name = fileName
        self.type = fileType
        self.sName = ''
        self.title = ''
        self.term = Dictionary()
        self.weight = Dictionary()

    def setTitle(self, title):
        '''set the title of the page'''

        self.title = title

    def stem(self):
        '''implement stemming algorithm'''
        split = self.name.split('.')
        self.sName = split[0] + '_stem' + '.txt'
        stemmer = stemming.PorterStemmer()
        with open(self.name) as f:
            while 1:
                output = ''
                word = ''
                line = f.readline()
                if line == '':
                    break
                for c in line:
                    if c.isalpha():
                        word += c.lower()
                    else:
                        if word:
                            output += stemmer.stem(word, 0, len(word) - 1)
                            word = ''
                        output += c.lower()
                with open(self.sName, 'a') as o:
                    o.write(output)

    def collection(self):
        '''extract term and term frequency'''
        with open(self.sName) as f:
            for line in f.readlines():
                # match word
                matchWord = re.compile('[A-Za-z]+')
                words = matchWord.findall(line)
                for word in words:
                    if self.term[word] == 0:
                        self.term[word] = 1
                    else:
                        self.term[word] += 1
                # match number
                matchNumber = re.compile('[0-9]+')
                numbers = matchNumber.findall(line)
                for number in numbers:
                    if self.term[number] == 0:
                        self.term[number] = 1
                    else:
                        self.term[number] += 1

    def getTerm(self):
        return self.term

    def getID(self):
        return self.docID

    def getUrl(self):
        return self.url

    def getTitle(self):
        return self.title

    def getWeight(self):
        return self.weight

    def setScore(self, score):
        self.score = score

    def getScore(self):
        return self.score

    def weightDoc(self, model, *args):
        '''calculate tf-idf for doc vector
            @para model: different weighting model
            "tf": weight = tf
            "tf-idf": weight = tf * idf
            "log": weight = (1 + log(tf)) * idf
            args: idf
        '''
        if model == 'tf':
            self.Weight = self.term
        if model == 'tf-idf':
            for idf in args:
                for key in self.term.keys():
                    self.weight[key] = self.term[key] * idf[key]

        if model == 'log':
            for idf in args:
                for k in self.term.keys():
                    self.weight[k] = (1 + math.log(self.term[k])) * idf[k]

    def normalizeDoc(self):
        ''''cosine nomalization'''
        length = 0
        for key in self.weight.keys():
            length += math.pow(self.weight[key], 2)
        length = math.sqrt(length)

        # normalize
        for key in self.weight.keys():
            self.weight[key] = self.weight[key] / length

    def readfile(self, number):
        '''@number: number of word to read'''
        with open(self.name) as f:
            content = f.read()
        match = re.compile("\w+")
        out = ""
        words = match.findall(content)
        for word in words:
            if number > 0:
                out = out + " " + word
                number -= 1
        return out
