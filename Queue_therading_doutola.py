#!/usr/bin/env python3
# --*-- coding:utf-8 --*--
# __Author__ Aaron

import requests
from lxml import etree
import os
from urllib import request
import re
import threading
import queue


# 生产者队列，主要获取doutola的图片url
class Producer(threading.Thread):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' \
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
               'Referer': 'https://ad.doubleclick.net/ddm/adi/N4864.2348101MICROADCN/B22107443.241567361;'
                          'sz=728x90;click=http://dsp.send.microad-cn.com/v2/g/cc?ep=85OYyNwYe3vcn4qxGtw4wdYFYzuHAitLirSaFVL60tiBRaMF5gOm2VZ2kn0SNZk1rMdMS-VG-NrmERYHJbQCRXW5_'
                          'g86f-Zz4&sct=https://adclick.g.doubleclick.net/aclk%3Fsa%3DL%26ai%3DChOE-7ue_XLKHINj2rQSryJ-wDbLur5lNs4TdjlDAjbcBEAEgAGCd-d-B3AWCARdjYS1wdWItODM3NjA0NDU1MjgzODM4M8gBCakCdL_'
                          '6GTv3gz6oAwGqBL0BT9AJgKYzNPcum7RcDhihtch1Dv9AYzoBKvoPzBT3-NlDQuEZXgyOmIsX2Bik5AptkFPC1PV-2a-WLoDM3WUo2tJnmWTt4qeFOyIN18MKs1_LXHbhjB-6gYorvIkUEDt20kxQk_'
                          'nRIXwyucYWRUr9iesrDo4DDmK6BW1gSbpMgpNEI5_BjmzyI7BDANxmGYhgVbgZMcLxtDweVDePEh6OnHCx8K1E4cHFqGphzS1Ok-JVTCniYNJFA1JJo_3PgAb6-6ji-ruztV-gBiGoB6a-G6gH2csbqAfPzBvYBwDSCAUIgGEQAQ%26num%3D1%26sig%3DAOD64'
                          '_0oyTnLuwcNPOLo7o-tT12NLGxX-w%26client%3Dca-pub-8376044552838383%26adurl%3D&r=;ord=[timestamp];dc_lat=;dc_rdid=;tag_for_child_directed_treatment=;tfua=?'
               }

    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Producer, self).__init__(*args, **kwargs)
        self.page_quene = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_quene.empty():
                break

            url = self.page_quene.get()
            self.pares_page(url)

    def pares_page(self, url):

        response = requests.get(url, headers=self.headers)
        # print(response.text)
        text = response.text
        html = etree.HTML(text)
        imgs = html.xpath('//div[@class="col-sm-9"]//img[@class!="gif"]')
        for img in imgs:
            img_url = img.get('data-original')
            alt = img.get('alt')
            # windows 下文件名不能是一些特殊字符
            alt = re.sub(r'\??\.。!！\*', '', alt)
            suffix = os.path.splitext(img_url)[1]
            filename = alt + suffix
            # request.urlretrieve(img_url, "images/" + filename)
            self.img_queue.put((img_url, filename))


# 消费者队列，只负责下载图片的下载
class Consumer(threading.Thread):
    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break

            img_url, filename = self.img_queue.get()
            # print('img_url:',img_url,'filename:',filename)
            request.urlretrieve(img_url, "images/" + filename)
            print(filename + '下载完成')


def main():
    page_queue = queue.Queue(100)
    img_queue = queue.Queue(1000)
    for i in range(1, 101):
        url = 'https://www.doutula.com/article/list/?page=%d' % i
        page_queue.put(url)


    for x in range(5):
        t = Producer(page_queue, img_queue)
        t.start()

    for x in range(5):
        t = Consumer(page_queue, img_queue)
        t.start()


if __name__ == '__main__':
    main()
