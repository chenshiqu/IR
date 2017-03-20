# encoding: UTF-8
import stemming


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
                words = line.split()
                for word in words:
                    token = word.split('/')
                    for t in token:
                        t = t.rstrip(',.:-=')
                        if t != '':
                            if self.term[t] == 0:
                                self.term[t] = 1
                            else:
                                self.term[t] += 1

    def getTerm(self):
        return self.term

    def getID(self):
        return self.docID

    def getUrl(self):
        return self.url
