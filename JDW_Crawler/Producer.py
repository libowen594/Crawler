#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from pymongo import MongoClient
import requests
from Config import Config
import threading
import bs4

urls = ["http://jandan.net/girl"]
conn = MongoClient('localhost', 27017)
db = conn.xxoo
my_set = db.xxoo_data
index_data = my_set.find().sort([("index", -1)]).limit(1)
current_url_data = [i for i in my_set.find({"is_latest": True})]
if index_data:
    index = index_data[0]["index"]
else:
    index = 0
if current_url_data:
    current_url = current_url_data[0]["url"]
else:
    current_url = None
g_lock = threading.Lock()


def get_latest_url():
    UserAgent = Config().getHeaders()
    headers = {'User-Agent': UserAgent,
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                         "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9",
               "Connection": "keep-alive",
               "Host": "jandan.net",
               }
    url = urls[0]
    try:
        response = requests.get(url, headers=headers, timeout=5)
    except Exception as http:
        print(http)
        sys.exit(0)
    soup = bs4.BeautifulSoup(response.text, "html5lib")
    latest_url = f"http:{soup.select('.view_img_link')[0].get('href')}"
    return latest_url


class Producer(threading.Thread):
    def run(self):
        print("线程启动………………")
        UserAgent = Config().getHeaders()
        headers = {'User-Agent': UserAgent,
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                             "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Accept-Encoding": "gzip, deflate",
                   "Accept-Language": "zh-CN,zh;q=0.9",
                   "Connection": "keep-alive",
                   "Host": "jandan.net",
                   }
        global urls
        global index
        global current_url
        latest_url = get_latest_url()
        print(f"latest_url:{latest_url}")
        while len(urls) != 0:
            g_lock.acquire()
            url = urls.pop()
            g_lock.release()
            try:
                response = requests.get(url, headers=headers, timeout=5)
            except Exception as http:
                print(http)
                continue
            soup = bs4.BeautifulSoup(response.text, "html5lib")
            new_url = soup.select('.cp-pagenavi')[0].find_all(title="Older Comments")
            if new_url:
                link = f'http:{new_url[0].get("href")}'
                if link not in urls and link != url:
                    urls.append(link)
            else:
                continue
            real_urls = soup.select('.view_img_link')
            for u in real_urls:
                real_url = f'http:{u.get("href")}'
                if real_url != current_url:
                    my_set.update_one({"url": real_url}, {"$set": {"is_latest": False},
                                                          "$setOnInsert": {"index": index, "is_download": 0}},
                                      upsert=True)
                    print(real_url)
                    index += 1
                #     my_set.insert_one({"index": index, "url": real_url, "is_download": 0, "is_latest": False})
                # else:
                #     my_set.update_one({"url": latest_url}, {"$set": {"is_latest": True}})
                #     my_set.update_one({"url": current_url}, {"$set": {"is_latest": False}})
                #     conn.close()
                #     sys.exit(0)
        else:
            #     my_set.update_one({"url": latest_url}, {"$set": {"is_latest": True}})
            #     my_set.update_one({"url": current_url}, {"$set": {"is_latest": False}})
            conn.close()


if __name__ == '__main__':
    p = Producer()
    p.start()
