# encoding: UTF-8
import urllib.request
import urllib
import re
from collections import deque


class Spider:
    '''a specific crawler for http://lyle.smu.edu/~fmoore'''

    def __init__(self, url, limit):
        self.queue = deque()
        self.visited = set()  # set of url that have been fetched
        self.disallow = []
        self.url = url
        self.limit = limit

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

            urlop = urllib.request.urlopen(url)
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
                # if 'http' in x and x not in self.visited:
                for disallow in self.disallow:
                    mark = re.compile(disallow)
                    if mark.match(x):
                        break
                    self.queue.append(x)
                    print('add to queue---> ' + x)


if __name__ == '__main__':
    '''main program'''
    spider = Spider(url='http://lyle.smu.edu/~fmoore', limit=1)
    spider.fetch()
