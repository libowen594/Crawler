#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
from pymongo import MongoClient
import requests
from Config import Config
import base64
import threading

conn = MongoClient('localhost', 27017)
db = conn.xxoo
my_set = db.xxoo_data
g_lock = threading.Lock()
os.makedirs("./data/img", exist_ok=True)
urls = []
data = [i for i in my_set.find({"is_download": 0})]
if data:
    for i in data:
        urls.append(i["url"])
else:
    conn.close()
    sys.exit(0)


class Consumer(threading.Thread):
    def run(self):
        print("线程启动………………")
        UserAgent = Config().getHeaders()
        headers = {'User-Agent': UserAgent,
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                             "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Accept-Encoding": "gzip, deflate",
                   "Accept-Language": "zh-CN,zh;q=0.9",
                   "Connection": "keep-alive",
                   "Host": "wx4.sinaimg.cn",
                   }
        while len(urls) != 0:
            g_lock.acquire()
            url = urls.pop()
            g_lock.release()
            filename = url.split("/")[-1]
            try:
                response = requests.get(url, headers=headers, timeout=5)
            except Exception as http:
                print(http)
                continue
            if response.status_code == 200:
                img = response.content
            else:
                my_set.update({"url": url}, {"$set": {"is_download": 2}})
                continue
            with open(os.path.join("./data/img", filename), "wb+") as f:
                f.write(img)
            base64_ = base64.b64encode(img)
            my_set.update_one({"url": url}, {"$set": {"is_download": 1, "base64": base64_}})
        else:
            conn.close()


if __name__ == '__main__':
    for k in range(0, 5):
        c = Consumer()
        c.start()
