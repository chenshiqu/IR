# encoding: UTF-8
import stemming
import re


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
                matchWord = re.compile('[A-Za-z]+')
                words = matchWord.findall(line)
                for word in words:
                    if self.term[word] == 0:
                        self.term[word] = 1
                    else:
                        self.term[word] += 1
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
