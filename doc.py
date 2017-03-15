# encoding: UTF-8
import stemming


class Document:
    ''' a describe of a web page
        @author: Shiqu Chen
    '''

    def __init__(self, docID, fileName, fileType):

        self.docID = docID
        self.name = fileName
        self.type = fileType
        self.sName = ''
        self.title = ''

    def setTitle(self, title):
        self.title = title

    def stem(self):
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
