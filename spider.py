# encoding: UTF-8
import urllib.request
import urllib
from urllib import parse
import re
from collections import deque


class Spider:
    '''a specific crawler for http://lyle.smu.edu/~fmoore'''

    def __init__(self, url, limit):
        '''paramaters
        @url :the begin url
        @limit : the limit on the number of pages to be retrieve
        '''
        self.queue = deque()  # containing urls yet to be fetched
        self.visited = set()  # set of url that have been fetched
        self.disallow = []    # containing urls that disallow to access
        self.url = url        # begin page to be crawled
        self.limit = limit    # limit on the number of pages to be retrieve

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
                print(disallow_url)
                self.disallow.append(disallow_url)

    def checkPermit(self, url):
        '''check weather access the url is disallow
            @return 0: allow
                    1: disallow
        '''
        for disallow_url in self.disallow:
            mark = re.compile(disallow_url)
            if mark.match(url):
                return 1
        return 0

    def urlFormalize(self, rawUrl):
        ''' ensure urls do not go out of root direction
            transfer relative url to absolute url
        '''
        components = parse.urlparse(rawUrl)
        formalUrl = rawUrl
        if components.scheme == "http":  # absolute url
            if components.netloc != 'lyle.smu.edu':  # out of root
                formalUrl = ''
            else:
                mark = re.compile('~fmoore')
                if mark.match(components.path):  # out of root
                    formalUrl = ''
        elif components.scheme == "":  # relative url
            # transfer relative url to absolute url
            formalUrl = parse.urljoin(self.url + '/', rawUrl)
        else:
            formalUrl = ''

        return formalUrl

    def fetch(self):
        '''fetch url'''
        self.queue.append(self.url)
        cnt = 0

        self.robots()  # fetch robots.txt

        while self.queue:
            url = self.queue.popleft()
            self.visited |= {url}  # remark as visited

            print('already fetch: ' + str(cnt) + '  fetching <----' + url)

            cnt += 1
            if cnt > self.limit:
                break

            urlop = urllib.request.urlopen(url)  # crawling data
            if 'html' not in urlop.getheader('Content-Type'):
                continue

            # address exception
            try:
                data = urlop.read().decode('utf-8')
            except:
                continue

            # fetch url from page
            linkre = re.compile('href="(.+?)"')
            for x in linkre.findall(data):
                print(x)
                formalUrl = self.urlFormalize(x)
                if formalUrl != '':
                    self.queue.append(formalUrl)
                    print('add to queue---> ' + formalUrl)


if __name__ == '__main__':
    '''main process'''
    spider = Spider(url='http://lyle.smu.edu/~fmoore', limit=1)
    spider.fetch()
