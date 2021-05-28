#!/usr/bin/env python
# -*- coding:utf-8 -*-
from pymongo import MongoClient
import requests
from pymongo import MongoClient
import time

# response = requests.get("http://floor.huluxia.com/post/favorite/list/ANDROID/2.0?start=0&count=20&user_id=23079055",
#                         timeout=5)
# print(response.json())

conn = MongoClient('localhost', 27017)
db = conn.xxoo
my_set = db.hlx_crawler_data
# my_set.insert_one({"blog_cont": "abcdef", "title": "《My Test》"})
my_set.update_one({"blog_cont": "123"}, {"$setOnInsert": {"other": "hello world!"}}, upsert=True)
