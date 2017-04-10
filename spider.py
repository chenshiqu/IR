# encoding: UTF-8
import urllib.request
import urllib
from urllib import parse
import re
from collections import deque
from bs4 import BeautifulSoup
from doc import Document
from doc import Dictionary
import operator


class Spider:
    ''' a specific crawler for http://lyle.smu.edu/~fmoore
        @author Shiqu Chen
    '''

    def __init__(self, url, limit, stop):
        ''' paramaters
            @url :the begin url
            @limit : the limit on the number of pages to be retrieve
        '''
        self.queue = deque()    # containing urls yet to be fetched
        self.visited = set()    # set of url that have been fetched
        self.disallow = []      # containing urls that disallow to access
        self.allUrl = set()     # containing all url in the root url
        self.outUrl = set()     # containing all url that out root
        self.brokenUrl = set()  # saving broken url
        self.image = set()      # saving image url
        self.application = set()        # saving application file url
        self.url = url          # begin page to be crawled
        self.limit = limit      # limit on the number of pages to be retrieve
        self.docNumber = 0
        self.docList = []
        self.term = Dictionary()
        self.stop = stop          # stop word

    def robots(self):
        '''fetch robots.txt and get disallow url'''
        mark = re.compile(r'Disallow:')
        robotsUrl = self.url + '/robots.txt'
        urlop = urllib.request.urlopen(robotsUrl)
        for line in urlop:
            line = line.decode('utf-8')
            if mark.match(line):
                disallow = re.split(': /', line)
                disallow_url = disallow[1].strip()
                # print(disallow_url)
                self.disallow.append(disallow_url)

    def checkPermit(self, url):
        ''' check weather access the url is disallow
            @return 0: allow
                    1: disallow
        '''
        for disallow_url in self.disallow:
            mark = re.compile(disallow_url)
            if mark.match(url):
                return 1
        return 0

    def urlFormalize(self, currentUrl, rawUrl):
        ''' ensure urls do not go out of root direction
            transfer relative url to absolute url
        '''
        components = parse.urlparse(rawUrl)
        formalUrl = rawUrl
        if self.checkPermit(components.path) == 1:  # if url is disallow
            formalUrl = ''
            return formalUrl
        # absolute url
        if components.scheme == "http" or components.scheme == "https":
            if components.netloc != 'lyle.smu.edu':  # out of root
                self.outUrl |= {rawUrl}
                formalUrl = ''
                print('    out of root')
            else:
                mark = re.compile('/~fmoore')
                if mark.match(components.path) is None:  # out of root
                    self.outUrl |= {rawUrl}
                    formalUrl = ''
                    print("    out of root")
        elif components.scheme == "":  # relative url
            # transfer relative url to absolute url
            formalUrl = parse.urljoin(currentUrl, rawUrl)
            mark = re.compile(self.url)
            if mark.match(formalUrl) is None:  # out of root
                formalUrl = ''
        else:
            formalUrl = ''

        # if url end with /, add index.html to the url
        # if formalUrl != '' and formalUrl[-1] == '/':
        #    formalUrl = formalUrl + 'index.html'

        return formalUrl

    def urlDuplicate(self, url):
        ''' eliminate duplicate url
            @return 0: not duplicate
                    1: duplicate
        '''
        duplication = 0
        if url in self.visited:
            duplication = 1
        if url in self.queue:
            duplication = 1
        return duplication

    def parse(self, url, contentType, data):
        ''' address response data
            @contentType
            @data
            @return 1:duplicate
        '''
        if 'html' in contentType:
            # extract text from html file
            soup = BeautifulSoup(data, "lxml")
            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            # get title
            title = soup.title.string
            # get text
            text = soup.body.get_text()
            # break into lines and remove leading adn trailing spaces
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = []
            for line in lines:
                for phrase in line.split("  "):
                    chunks.append(phrase.strip())
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # write to local file
            self.docNumber += 1
            filename = "doc_" + str(self.docNumber) + ".txt"
            with open(filename, 'w') as f:
                f.write(text)
            document = Document(url, self.docNumber, filename, 'html')
            document.setTitle(title)
            # self.docList.append(document)

        else:      # txt file
            lines = (line.strip() for line in data.splitlines())
            # break multi-headlines into a line each
            chunks = []
            for line in lines:
                for phrase in line.split("  "):
                    chunks.append(phrase.strip())
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # write to local file
            self.docNumber += 1
            filename = "doc_" + str(self.docNumber) + ".txt"
            with open(filename, "w") as f:
                f.write(text)
            document = Document(url, self.docNumber, filename, 'txt')
            # self.docList.append(document)

        # term stemming and collection
        document.stem()
        document.collection()
        # duplicate detection
        duplicate = 0
        for d in self.docList:
            print(d.getID())
            if self.duplicateDetection(document, d) == 1:
                print('duplicate to %d' % d.getID())
                duplicate = 1
                break
        if duplicate == 0:
            self.docList.append(document)
            return 0
        else:
            return 1

    def fetch(self):
        '''whole fetching process'''

        self.queue.append(self.url)
        cnt = 0

        self.robots()  # fetch robots.txt

        while self.queue:
            # fetch url
            url = self.queue.popleft()
            if url in self.visited:  # url has been crawled
                continue
            self.visited |= {url}  # remark as visited

            print('already fetch: ' + str(cnt) + '  fetching <----' + url)

            # limit
            cnt += 1
            if cnt > self.limit:
                break

            # crawling data
            req = urllib.request.Request(url)
            try:
                urlop = urllib.request.urlopen(req)
            except urllib.error.HTTPError:
                self.brokenUrl |= {url}
                print("  HTTPError")
                print("----------------------------------------")
                continue
            except urllib.error.URLError:
                self.brokenUrl |= {url}
                continue

            # deal with different response file type
            fileType = urlop.getheader('Content-Type')
            if 'text' in fileType:  # text file include txt, htm, html
                print('   text file %s' % urlop.geturl())
                # address exception
                try:
                    data = urlop.read().decode('utf-8')
                except:
                    print("------------------------------------------")
                    continue

                # parse data
                t = self.parse(urlop.geturl(), fileType, data)
                if t == 1:
                    print('content duplicate')
                    print('------------------------------------------')
                    continue

                # fetch url from page
                linkre = re.compile('href="(.+?)"')
                for x in linkre.findall(data):
                    print("   fetch %s" % x)
                    self.allUrl |= {x}
                    formalUrl = self.urlFormalize(urlop.geturl(), x)
                    if formalUrl != '':
                        d = self.urlDuplicate(formalUrl)  # duplicattion check
                        if d == 0:
                            self.queue.append(formalUrl)
                            print('   add to queue---> ' + formalUrl)
                        else:
                            print("    duplication")

            elif 'image' in fileType:  # image
                print("   image file")
                self.image |= {url}
                print("----------------------------------------")
                continue
            else:                      # other type like pdf
                print("   application")
                self.application |= {url}
                print('-----------------------------------------')
                continue

            print('------------------------------------------')

    def collection(self):
        '''term collection'''
        for d in self.docList:
            dTerm = d.getTerm()
            for key in dTerm.keys():
                if self.term[key] != 0:
                    self.term[key] += dTerm[key]
                else:
                    self.term[key] = dTerm[key]
        # print(self.term)

    def duplicateDetection(self, doc1, doc2):
        ''' using k-shingles to detect near-duplication
            here k=1
            doc1 and doc2: document object
            @return 1:duplicate 0: not duplicate
        '''
        dTerm1 = doc1.getTerm()
        dTerm2 = doc2.getTerm()
        termSet1 = set(dTerm1.keys())
        termSet2 = set(dTerm2.keys())

        Jaccard = len(termSet1 & termSet2) / len(termSet1 | termSet2)
        print("Jaccard: %f" % Jaccard)
        if Jaccard > 0.9:
            return 1
        else:
            return 0

    def stopwordEliminate(self):
        '''delete stop word from the dictionary'''
        for word in self.stop:
            if word in self.term.keys():
                self.term.pop(word)

    def report(self):
        print('visited url')
        for i in self.visited:
            print(i)
        print('---------------------')
        print('queue')
        print(self.queue)
        print('------------------------------------')
        print('out root url:')
        for url in self.outUrl:
            print(url)
        print('--------------------------------------')
        print('all urls')
        for url in self.allUrl:
            print(url)
        '''
        print('stemming........................')
        for d in self.docList:
            d.stem()
        print('------------------------------------------')
        print('collection processing......................')
        for d in self.docList:
            d.collection()
            # print(d.getTerm())
        '''
        print('-----------------------------------------')
        print('broken url')
        for url in self.brokenUrl:
            print(url)
        print('---------------------------------')
        print('image')
        for url in self.image:
            print(url)
        print('---------------------------------')
        print('title')
        for doc in self.docList:
            print(doc.getID())
            print(doc.getUrl())
            print(doc.getTitle())
        print('------------------------------')

        self.collection()

        # delete stop word
        self.stopwordEliminate()

        # ranking
        print('-------------------------------------------------------')
        sorted_term = sorted(self.term.items(), key=operator.itemgetter(1))
        # print(sorted_term)
        i = 1
        while i <= 20:
            print(sorted_term[-i])
            i += 1


if __name__ == '__main__':
    '''main process'''
    Limit = 40
    stopWord = ['to']
    URL = 'http://lyle.smu.edu/~fmoore'
    spider = Spider(url=URL, limit=Limit, stop=stopWord)
    spider.fetch()
    spider.report()
