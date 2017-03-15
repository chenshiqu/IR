# encoding: UTF-8
import urllib.request
import urllib
from urllib import parse
import re
from collections import deque
from bs4 import BeautifulSoup
from doc import Document


class Spider:
    ''' a specific crawler for http://lyle.smu.edu/~fmoore
        @author Shiqu Chen
    '''

    def __init__(self, url, limit):
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
        if components.scheme == "http":  # absolute url
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

    def parse(self, contentType, data):
        ''' address response data
            @contentType
            @data
            @return
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
            document = Document(self.docNumber, filename, 'html')
            document.setTitle(title)
            self.docList.append(document)

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
            document = Document(self.docNumber, filename, 'txt')
            self.docList.append(document)

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
                self.parse(fileType, data)

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

    def report(self):
        print('visited url')
        for i in self.visited:
            print(i)
        print('---------------------')
        print('queue')
        print(self.queue)
        for d in self.docList:
            d.stem()


if __name__ == '__main__':
    '''main process'''
    spider = Spider(url='http://lyle.smu.edu/~fmoore', limit=40)
    spider.fetch()
    spider.report()
