#!/usr/bin/env python3
# --*-- coding:utf-8 --*--
# __Author__ Aaron

import requests
from lxml import etree
import csv
import threading
import queue


# 生产者队列，主要获取百思不得姐段子的url
class BSSpider(threading.Thread):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' \
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
               }

    def __init__(self, page_queue, joke__queue, *args, **kwargs):
        super(BSSpider, self).__init__(*args, **kwargs)
        self.base_domain = "http://www.budejie.com/"
        self.page_quene = page_queue
        self.joke_queue = joke__queue

    def run(self):
        while True:
            if self.page_quene.empty():
                break

            url = self.page_quene.get()
            self.pares_page(url)

    def pares_page(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' \
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
                   }
        response = requests.get(url, headers=headers)
        text = response.text
        html = etree.HTML(text)
        descs = html.xpath('//div[@class="j-r-list-c-desc"]')
        for desc in descs:
            jokes = desc.xpath('.//text()')
            # print(str(jokes).strip())
            joke = '\n'.join(jokes).strip()
            # print(">>>"+joke)
            link = self.base_domain + desc.xpath('.//a/@href')[0]
            # print(link)
            self.joke_queue.put((joke, link))

        print('=' * 30 + '第%s页下载完成' % url.split('/')[-1] + '=' * 30)



# 消费者队列，只负责下载百思不得姐段子
class BSWriter(threading.Thread):
    def __init__(self, joke_queue, writer, gLock, *args, **kwargs):
        super(BSWriter, self).__init__(*args, **kwargs)
        self.joke_queue = joke_queue
        self.writer = writer
        self.lock = gLock

    def run(self):
        while True:
            try:
                joke_info = self.joke_queue.get(timeout=40)
                joke, link = joke_info
                self.lock.acquire()
                self.writer.writerow((joke, link))
                self.lock.release()
                print('保存一条')
            except:
                break




def main():
    page_queue = queue.Queue(10)
    joke_queue = queue.Queue(500)
    gLock = threading.Lock()
    fp = open('bsbdj.csv', 'a', newline='', encoding='utf-8')
    writer = csv.writer(fp)
    writer.writerow(('content', 'link'))

    for i in range(1, 11):
        url = 'http://www.budejie.com/%d' % i
        page_queue.put(url)

    for x in range(5):
        t = BSSpider(page_queue, joke_queue)
        t.start()

    for x in range(5):
        t = BSWriter(joke_queue, writer, gLock)
        t.start()


if __name__ == '__main__':
    main()
