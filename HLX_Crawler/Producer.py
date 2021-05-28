import sys
from pymongo import MongoClient
import requests
import threading
import time

urls = ["http://floor.huluxia.com/post/list/ANDROID/2.1?start=0&count=0&cat_id=56&tag_id=5601&sort_by=1"]
conn = MongoClient('localhost', 27017)
db = conn.xxoo
data_set = db.hlx_data
info_set = db.hlx_userInfo
g_lock = threading.Lock()


class Producer(threading.Thread):
    def run(self):
        global urls
        while True:
            g_lock.acquire()
            if len(urls) != 0:
                url = urls.pop()
                print(url)
                g_lock.release()
            else:
                g_lock.release()
                sys.exit(0)
            try:
                response = requests.get(url, timeout=5)
            except Exception as http:
                print(http)
                continue
            if response.status_code == 200:
                start = response.json()["start"]
                if url == f"http://floor.huluxia.com/post/list/ANDROID/2.1?start={start}&count=0&cat_id=56&tag_id=5601&sort_by=1":
                    sys.exit(0)
                urls.append(
                    f"http://floor.huluxia.com/post/list/ANDROID/2.1?start={start}&count=0&cat_id=56&tag_id=5601&sort_by=1")
                if response.json()["posts"] is not None:
                    for info in response.json()["posts"]:
                        postId = info["postID"]
                        if info["voice"] is not None:
                            voice = eval(info["voice"])
                            video = f'{voice["videohost"]}{voice["videofid"]}'
                        else:
                            video = None
                        createTime = time.strftime("%Y-%m-%d %H:%M:%S",
                                                   time.localtime(int(str(info["createTime"])[:-3])))
                        title = info["title"]
                        images = info["images"]
                        tagid = info["tagid"]
                        userID = info["user"]["userID"]
                        hit = info["hit"]
                        commentCount = info["commentCount"]
                        name = info["user"]["nick"]
                        age = info["user"]["age"]
                        gender = info["user"]["gender"]
                        if gender == 1:
                            sex = "女"
                        elif gender == 2:
                            sex = "男"
                        else:
                            sex = "未知"
                        identityTitle = info["user"]["identityTitle"]
                        data = {"title": title, "user_id": userID, "images": images, "video": video,
                                "hit": hit, "commentCount": commentCount, "tagid": tagid,
                                "createTime": createTime, "updateTime": time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                      time.localtime(int(
                                                                                          str(time.time()).split(".")[
                                                                                              0]))),
                                }
                        data_set.update_one({"post_id": postId}, {"$set": data,
                                                                  "$setOnInsert": {"download": False}}, upsert=True)
                        user_data = {"name": name, "age": age, "gender": sex, "identityTitle": identityTitle}
                        info_set.update_one({"user_id": userID}, {"$set": user_data}, upsert=True)
                else:
                    continue
            else:
                break


if __name__ == '__main__':
    for i in range(0, 2):
        P = Producer()
        P.start()
