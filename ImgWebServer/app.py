import base64
import json
import os
import requests
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from Config import Config

app = Flask(__name__,
            template_folder='./templates',
            static_folder='./static',
            )


@app.route('/')
def home():
    return render_template('homePage.html')


def get_url(index):
    conn = MongoClient('localhost', 27017)
    db = conn.xxoo
    my_set = db.xxoo_data
    data = [i for i in my_set.find({"index": index}, {"_id": 0, "url": 1})]
    count = my_set.estimated_document_count()
    conn.close()
    if data:
        return data[0]["url"], count
    else:
        return None, count


@app.route('/getTupian', methods=["POST"])
def get_tupian():
    if request.method == "POST":
        index = request.json.get("index")
        if not isinstance(index, int):
            return json.dumps({"data": None, "msg": "请求参数类型错误", "code": -4001, "maxindex": 0}, ensure_ascii=False)
        try:
            url, maxindex = get_url(index)
            if index == 0:
                return json.dumps({"data": None, "msg": "已经是第一张照片了", "code": -5001, "maxindex": maxindex},
                                  ensure_ascii=False)
        except Exception:
            return json.dumps({"data": None, "msg": "获取照片url错误", "code": -3001, "maxindex": 0}, ensure_ascii=False)
    else:
        return json.dumps({"data": None, "msg": "请求方式错误", "code": -2001, "maxindex": 0}, ensure_ascii=False)
    if url:
        UserAgent = Config().getHeaders()
        headers = {'User-Agent': UserAgent,
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                             "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                   "Accept-Encoding": "gzip, deflate",
                   "Accept-Language": "zh-CN,zh;q=0.9",
                   "Connection": "keep-alive",
                   "Host": "wx4.sinaimg.cn",
                   }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            filename = url.split("/")[-1]
            shotname, extension = os.path.splitext(filename)
            if response.status_code == 200:
                img = response.content
                base64_ = str(base64.b64encode(img), encoding='utf-8')
                return json.dumps(
                    {"data": f"data:image/{extension};base64,{base64_}", "msg": "", "code": 0, "maxindex": maxindex},
                    ensure_ascii=False)
        except Exception as e:
            print(e)
            return json.dumps({"data": None, "msg": "获取照片错误", "code": -1001, "maxindex": maxindex}, ensure_ascii=False)
    else:
        return json.dumps({"data": None, "msg": "已经是最后一张了", "code": -1, "maxindex": maxindex}, ensure_ascii=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
